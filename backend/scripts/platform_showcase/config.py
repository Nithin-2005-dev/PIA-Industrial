"""
===============================================================================

Platform Showcase Configuration

===============================================================================

Loads configuration from

1. CLI
2. Environment variables
3. Defaults

No stage should read environment variables directly.

===============================================================================
"""

from __future__ import annotations

import argparse
import os

from dataclasses import dataclass
from pathlib import Path


# ============================================================================
# Configuration
# ============================================================================


@dataclass(slots=True)
class ShowcaseConfig:

    # ------------------------------------------------------------------
    # GitHub
    # ------------------------------------------------------------------

    repository: str

    branch: str

    commit_limit: int

    github_token: str | None

    tenant_id: str

    # ------------------------------------------------------------------
    # Output
    # ------------------------------------------------------------------

    output_directory: Path

    export_json: bool

    export_markdown: bool

    save_pipeline: bool

    # ------------------------------------------------------------------
    # Console
    # ------------------------------------------------------------------

    verbose: bool

    show_lineage: bool

    show_graph: bool

    show_histograms: bool

    color: bool

    # ------------------------------------------------------------------
    # Performance
    # ------------------------------------------------------------------

    profile: bool

    timing: bool

    benchmark: bool

    # ------------------------------------------------------------------
    # Future Layers
    # ------------------------------------------------------------------

    enable_expertise: bool

    enable_reasoning: bool

    enable_decision: bool


# ============================================================================
# Parser
# ============================================================================


def _parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        prog="platform_showcase",
        description="PIA Complete Platform Showcase",
    )

    parser.add_argument(
        "--repo",
        default=os.getenv(
            "PIA_REPOSITORY",
            "facebook/react",
        ),
    )

    parser.add_argument(
        "--branch",
        default=os.getenv(
            "PIA_BRANCH",
            "main",
        ),
    )

    parser.add_argument(
        "--commits",
        type=int,
        default=int(
            os.getenv(
                "PIA_COMMIT_LIMIT",
                os.getenv(
                    "PIA_COMMITS",
                    "100",
                ),
            )
        ),
    )

    parser.add_argument(
        "--tenant",
        default=os.getenv(
            "PIA_TENANT",
            "default",
        ),
    )

    parser.add_argument(
        "--output",
        default=os.getenv(
            "PIA_OUTPUT",
            "outputs/showcase",
        ),
    )

    parser.add_argument(
        "--json",
        action="store_true",
    )

    parser.add_argument(
        "--markdown",
        action="store_true",
    )

    parser.add_argument(
        "--save",
        action="store_true",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
    )

    parser.add_argument(
        "--lineage",
        action="store_true",
    )

    parser.add_argument(
        "--graph",
        action="store_true",
    )

    parser.add_argument(
        "--histograms",
        action="store_true",
    )

    parser.add_argument(
        "--profile",
        action="store_true",
    )

    parser.add_argument(
        "--timing",
        action="store_true",
    )

    parser.add_argument(
        "--benchmark",
        action="store_true",
    )

    parser.add_argument(
        "--no-color",
        action="store_true",
    )

    return parser


# ============================================================================
# Load
# ============================================================================


def load_config() -> ShowcaseConfig:

    parser = _parser()

    args = parser.parse_args()

    token = (
        os.getenv("GITHUB_TOKEN")
        or os.getenv("GH_TOKEN")
    )

    output = Path(args.output)

    output.mkdir(
        parents=True,
        exist_ok=True,
    )

    return ShowcaseConfig(

        repository=args.repo,

        branch=args.branch,

        commit_limit=args.commits,

        github_token=token,

        tenant_id=args.tenant,

        output_directory=output,

        export_json=args.json,

        export_markdown=args.markdown,

        save_pipeline=args.save,

        verbose=args.verbose,

        show_lineage=args.lineage,

        show_graph=args.graph,

        show_histograms=args.histograms,

        color=not args.no_color,

        profile=args.profile,

        timing=args.timing,

        benchmark=args.benchmark,

        enable_expertise=False,

        enable_reasoning=False,

        enable_decision=False,
    )
