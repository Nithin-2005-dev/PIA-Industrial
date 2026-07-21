"""
===============================================================================

Platform Showcase UI

===============================================================================

Responsible only for rendering.

No business logic.

No Observation logic.

No Measurement logic.

No Evidence logic.

===============================================================================
"""

from __future__ import annotations

import shutil
from typing import Any


# ============================================================================
# Terminal
# ============================================================================

WIDTH = shutil.get_terminal_size((120, 40)).columns


# ============================================================================
# ANSI Colors
# ============================================================================

class Color:

    RESET = "\033[0m"

    BOLD = "\033[1m"

    DIM = "\033[2m"

    RED = "\033[91m"

    GREEN = "\033[92m"

    YELLOW = "\033[93m"

    BLUE = "\033[94m"

    MAGENTA = "\033[95m"

    CYAN = "\033[96m"

    WHITE = "\033[97m"


def c(text: Any, color: str) -> str:
    return color + str(text) + Color.RESET


# ============================================================================
# Basic Layout
# ============================================================================

def line(char: str = "="):
    print(char * WIDTH)


def separator():
    print("-" * WIDTH)


def blank():
    print()


# ============================================================================
# Banner — shows the full canonical architecture
# ============================================================================

MODULE_DISPLAY_NAMES: dict[str, str] = {
    "observation": "Observation Layer",
    "measurement": "Measurement Layer",
    "evidence": "Evidence Layer",
    "estimation": "Expertise Layer",
    "knowledge": "Knowledge Layer",
    "graph": "Knowledge Graph Layer",
    "temporal": "Temporal Intelligence",
    "forecasting": "Forecasting Layer",
    "simulation": "Counterfactual Simulation Layer",
    "intelligence": "Organization Intelligence",
    "causal": "Causal Intelligence",
    "agent": "Reasoning Layer",
    "decision": "Decision Layer",
    "executive": "Executive Intelligence Report",
}

def banner(runtime):
    line()
    print(c("PIA LATENT ENGINE".center(WIDTH), Color.BOLD))
    print(c("COMPLETE PLATFORM SHOWCASE".center(WIDTH), Color.CYAN))
    line()
    print()
    print("Canonical Architecture")
    print()
    
    # We want to pull the canonical execution order from the runtime modules registry
    order = runtime.modules.startup_order()
    
    print(" GitHub")
    for module_name in order:
        display_name = MODULE_DISPLAY_NAMES.get(module_name, f"{module_name.title()} Layer")
        
        # Apply specific colors for emphasis
        if module_name == "graph":
            display_name = c(display_name, Color.CYAN)
        elif module_name in ("temporal", "forecasting", "simulation"):
            display_name = c(display_name, Color.YELLOW)
        elif module_name in ("intelligence", "causal"):
            display_name = c(display_name, Color.MAGENTA)
            
        print("    |")
        print("    v")
        print(f" {display_name}")
        
        # Add the specific hint for org intel
        if module_name == "intelligence":
            print(c("    |  (Ownership . Coverage . Concentration . Bus Factor", Color.DIM))
            print(c("    |   Successor . Knowledge Risk . Health . Recommendations)", Color.DIM))

    blank()
    line()


# ============================================================================
# Stage Header
# ============================================================================

def stage(index: int, total: int, title: str):

    blank()

    separator()

    print(c(f"[{index}/{total}] {title}", Color.CYAN))

    separator()


# ============================================================================
# Success / Warning / Error
# ============================================================================

def success(msg: str):
    print(c("[OK] " + msg, Color.GREEN))


def warning(msg: str):
    print(c("! " + msg, Color.YELLOW))


def error(msg: str):
    print(c("[ERR] " + msg, Color.RED))


# ============================================================================
# Metrics
# ============================================================================

def metric(name: str, value: Any):
    print(f"{name:<38} {value}")


# ============================================================================
# Section
# ============================================================================

def section(title: str):

    blank()

    print(c(title, Color.BOLD))


# ============================================================================
# Key / Value Table
# ============================================================================

def table(rows: list[tuple[str, Any]]):

    for key, value in rows:

        metric(key, value)


# ============================================================================
# Ranking
# ============================================================================

def ranking(title: str, values):

    section(title)

    if not values:

        print("  (empty)")

        return

    for idx, item in enumerate(values, start=1):

        print(f" {idx:>2}. {item}")


# ============================================================================
# Histogram
# ============================================================================

def histogram(title: str, histogram_data: dict):

    section(title)

    if not histogram_data:

        print("  (empty)")

        return

    maximum = max(histogram_data.values())

    for bucket in sorted(histogram_data):

        value = histogram_data[bucket]

        bar = "#" * int((value / maximum) * 40)

        print(f"{bucket:>6} | {bar} {value}")


# ============================================================================
# Progress Bar
# ============================================================================

def progress(title: str, current: int, total: int):

    if total <= 0:

        total = 1

    width = 40

    ratio = current / total

    filled = int(width * ratio)

    empty = width - filled

    print(
        f"{title:<20}"
        f"[{'#'*filled}{'.'*empty}] "
        f"{current}/{total}"
    )


# ============================================================================
# Dashboard Card
# ============================================================================

def card(title: str, rows: list[tuple[str, Any]]):

    separator()

    print(c(title, Color.BOLD))

    separator()

    table(rows)


# ============================================================================
# Final Summary
# ============================================================================

def summary(title: str, rows: list[tuple[str, Any]]):

    blank()

    line()

    print(c(title.center(WIDTH), Color.BOLD))

    line()

    table(rows)

    line()


# ============================================================================
# Lineage — traces canonical flow from Decision back to GitHub
# ============================================================================

def lineage(title: str, path: list[str] = None):

    blank()

    section(title)

    print()

    if not path:
        print("  (Path unavailable)")
        return

    print(f" {path[0]}")
    for step in path[1:]:
        print("      |")
        print("      v")
        
        # Apply specific colors for emphasis
        if "Graph" in step:
            step = c(step, Color.CYAN)
        elif step in ("Temporal Intelligence", "Forecasting Layer", "Counterfactual Simulation Layer"):
            step = c(step, Color.YELLOW)
        elif step in ("Organization Intelligence", "Causal Intelligence"):
            step = c(step, Color.MAGENTA)
            
        print(f" {step}")


# ============================================================================
# Future Layer Placeholder
# ============================================================================

def future_layer(name: str):

    separator()

    print(c(name, Color.MAGENTA))

    print()

    print(" Not Implemented Yet")

    separator()
