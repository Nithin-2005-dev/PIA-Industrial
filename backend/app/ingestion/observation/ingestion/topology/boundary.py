"""SubsystemBoundaryProvider — pluggable subsystem extraction.

A subsystem is a meaningful organizational unit inferred from a file path.
Providers are repository-agnostic. The engine never hardcodes directory names.

Architecture:
    SubsystemBoundaryProvider (abstract interface)
        ├── GitHubMonorepoProvider   — packages/*, apps/*
        ├── RustCratesProvider       — crates/*
        ├── NodePackagesProvider     — packages/*, apps/*, libs/*
        ├── PythonPackageProvider    — top-level python packages
        ├── GoModuleProvider         — module/package prefix
        └── FallbackProvider         — first meaningful path segment

Usage:
    resolver = SubsystemResolver.default()
    subsystem = resolver.resolve("packages/react-server/src/ReactFizzServer.js")
    # → "react-server"
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from pathlib import PurePosixPath


# ---------------------------------------------------------------------------
# Abstract interface
# ---------------------------------------------------------------------------


class SubsystemBoundaryProvider(ABC):
    """Infers the canonical subsystem name from a file path."""

    @abstractmethod
    def can_handle(self, path: str) -> bool:
        """Return True if this provider applies to the given path."""

    @abstractmethod
    def extract(self, path: str) -> str | None:
        """Return the subsystem name, or None if not extractable."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable provider name for traceability."""


# ---------------------------------------------------------------------------
# Concrete providers
# ---------------------------------------------------------------------------


class GitHubMonorepoProvider(SubsystemBoundaryProvider):
    """
    Handles monorepos where the subsystem is the directory immediately
    under a well-known root such as packages/, apps/, libs/, services/.

    Example:
        packages/react-server/src/ReactFizzServer.js  →  react-server
        apps/playground/index.ts                       →  playground
    """

    _ROOTS = {"packages", "apps", "libs", "services", "modules", "components"}

    @property
    def name(self) -> str:
        return "github_monorepo"

    def can_handle(self, path: str) -> bool:
        parts = PurePosixPath(path).parts
        return len(parts) >= 2 and parts[0].lower() in self._ROOTS

    def extract(self, path: str) -> str | None:
        parts = PurePosixPath(path).parts
        if len(parts) >= 2 and parts[0].lower() in self._ROOTS:
            return parts[1]
        return None


class RustCratesProvider(SubsystemBoundaryProvider):
    """
    Handles Rust workspaces where subsystems are crates.

    Example:
        crates/parser/src/lib.rs           →  parser
        compiler/crates/react_hir/src/...  →  react_hir
    """

    @property
    def name(self) -> str:
        return "rust_crates"

    def can_handle(self, path: str) -> bool:
        return "crates/" in path

    def extract(self, path: str) -> str | None:
        match = re.search(r"crates/([^/]+)", path)
        return match.group(1) if match else None


class NodePackagesProvider(SubsystemBoundaryProvider):
    """
    Handles Node.js / JavaScript monorepos.

    Example:
        packages/eslint-plugin-react-compiler/src/rules/...  →  eslint-plugin-react-compiler
    """

    _ROOTS = {"packages", "libs", "plugins", "components", "modules"}

    @property
    def name(self) -> str:
        return "node_packages"

    def can_handle(self, path: str) -> bool:
        parts = PurePosixPath(path).parts
        return len(parts) >= 2 and parts[0].lower() in self._ROOTS

    def extract(self, path: str) -> str | None:
        parts = PurePosixPath(path).parts
        if len(parts) >= 2 and parts[0].lower() in self._ROOTS:
            return parts[1]
        return None


class CompilerSubdirectoryProvider(SubsystemBoundaryProvider):
    """
    Handles repos where a top-level directory (e.g., 'compiler') wraps
    an inner monorepo with packages/ or crates/ under it.

    Example:
        compiler/packages/babel-plugin-react-compiler/...  →  babel-plugin-react-compiler
        compiler/crates/react_compiler_hir/...             →  react_compiler_hir
    """

    @property
    def name(self) -> str:
        return "compiler_subdirectory"

    def can_handle(self, path: str) -> bool:
        parts = PurePosixPath(path).parts
        if len(parts) < 3:
            return False
        inner = parts[1].lower()
        return inner in {"packages", "crates", "apps", "libs"}

    def extract(self, path: str) -> str | None:
        parts = PurePosixPath(path).parts
        if len(parts) >= 3 and parts[1].lower() in {"packages", "crates", "apps", "libs"}:
            return parts[2]
        return None


class FallbackProvider(SubsystemBoundaryProvider):
    """
    Last-resort provider: uses the first meaningful path segment.

    Skips hidden directories and single-character segments.
    """

    _SKIP = {".", "..", "src", "lib", "test", "tests", "dist", "build"}

    @property
    def name(self) -> str:
        return "fallback"

    def can_handle(self, path: str) -> bool:
        return True

    def extract(self, path: str) -> str | None:
        for part in PurePosixPath(path).parts[:-1]:  # exclude filename
            if (
                part not in self._SKIP
                and not part.startswith(".")
                and len(part) > 1
            ):
                return part
        return "root"


# ---------------------------------------------------------------------------
# Resolver — chains providers in priority order
# ---------------------------------------------------------------------------


class SubsystemResolver:
    """
    Chains providers in priority order.

    First provider whose can_handle() returns True is used.
    """

    def __init__(self, providers: list[SubsystemBoundaryProvider]) -> None:
        self._providers = providers

    @classmethod
    def default(cls) -> "SubsystemResolver":
        """Default provider chain covering Rust, Node, monorepo, and fallback."""
        return cls([
            RustCratesProvider(),
            CompilerSubdirectoryProvider(),
            GitHubMonorepoProvider(),
            NodePackagesProvider(),
            FallbackProvider(),
        ])

    def resolve(self, path: str) -> str:
        """Return the canonical subsystem name for a file path."""
        for provider in self._providers:
            if provider.can_handle(path):
                result = provider.extract(path)
                if result:
                    return result
        return "root"

    def resolve_with_provider(self, path: str) -> tuple[str, str]:
        """Return (subsystem_name, provider_name) for traceability."""
        for provider in self._providers:
            if provider.can_handle(path):
                result = provider.extract(path)
                if result:
                    return result, provider.name
        return "root", "fallback"
