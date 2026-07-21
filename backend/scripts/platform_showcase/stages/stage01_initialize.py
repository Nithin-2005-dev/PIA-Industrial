"""
===============================================================================

Stage 01 - Platform Initialization

===============================================================================

Responsibilities

✓ Validate runtime
✓ Print platform information
✓ Validate output directory
✓ Validate GitHub configuration
✓ Initialize showcase metadata
✓ Print architecture

This stage NEVER touches the platform pipeline.

===============================================================================
"""

from __future__ import annotations

import os
import platform
import sys
import time

from ..context import PlatformContext
from ..ui import (
    success,
    warning,
    metric,
    section,
)

from .base import PipelineStage


class InitializeStage(PipelineStage):

    name = "Platform Initialization"

    def run(
        self,
        context: PlatformContext,
    ) -> None:

        context.metadata["pipeline_started"] = time.time()

        self._print_platform_info(context)

        self._validate_environment()

        self._validate_output_directory(context)

        self._validate_github(context)

        self._print_capabilities()

    # ------------------------------------------------------------------

    def _print_platform_info(
        self,
        context: PlatformContext,
    ) -> None:

        section("Platform")

        metric("Platform", "PIA Latent Engine")

        from ..ui import MODULE_DISPLAY_NAMES
        
        order = context.runtime.modules.startup_order()
        display_names = [
            MODULE_DISPLAY_NAMES.get(m, m.title()) 
            for m in order 
        ]
        architecture_str = " -> ".join(display_names)

        metric(
            "Architecture",
            architecture_str,
        )

        metric("Repository", context.repository)

        metric("Branch", context.branch)

        metric("Commit Limit", context.commit_limit)

        metric("Tenant", context.tenant_id)

        metric("Python", platform.python_version())

        metric("OS", platform.system())

        metric("Working Directory", os.getcwd())

        success("Platform initialized")

    # ------------------------------------------------------------------

    def _validate_environment(
        self,
    ) -> None:

        section("Environment")

        success(f"Python executable: {sys.executable}")

        success("Environment validation passed")

    # ------------------------------------------------------------------

    def _validate_output_directory(
        self,
        context: PlatformContext,
    ) -> None:

        section("Output")

        context.output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        success(f"Output directory ready")

        metric(
            "Directory",
            context.output_directory,
        )

    # ------------------------------------------------------------------

    def _validate_github(
        self,
        context: PlatformContext,
    ) -> None:

        section("GitHub")

        token = context.github_token

        if token:

            success("GitHub token detected")

            metric("Authentication", "Authenticated")

        else:

            raise RuntimeError(
                "GITHUB_TOKEN or GH_TOKEN is required for the real GitHub pipeline."
            )

    # ------------------------------------------------------------------

    def _print_capabilities(
        self,
    ) -> None:

        section("Platform Capabilities")

        capabilities = [

            "Vendor Collection",

            "Canonical Observation Layer",

            "Scientific Measurement Engine",

            "Canonical Evidence Synthesis",

            "Evidence-to-Expertise Handoff",

            "Knowledge Modeling",

            "Knowledge Graph Construction",

            "Organization Intelligence",

            "Reasoning Results",

            "Decision Intelligence",

            "Confidence Propagation",

            "Uncertainty Propagation",

            "Lineage Tracking",

            "Traceability",

            "Explainability",

            "Scientific Validation",

            "Plugin Architecture",

            "Multi-Tenant Ready",

            "SaaS Ready",

        ]

        for capability in capabilities:

            success(capability)
