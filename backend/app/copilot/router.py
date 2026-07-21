"""Query Router for Industrial Intelligence.

Determines the intent of a user query to route it to the
correct retrieval and generation strategy.
"""
from __future__ import annotations

import re
from enum import Enum


class QueryIntent(Enum):
    """Types of user queries."""
    TROUBLESHOOTING = "troubleshooting"      # E.g., "Why did P-101 fail?"
    ASSET_STATUS = "asset_status"            # E.g., "What is the status of P-101?"
    MAINTENANCE_HISTORY = "maintenance_history"  # E.g., "Show work orders for P-101"
    GENERAL_KNOWLEDGE = "general_knowledge"  # E.g., "How does a centrifugal pump work?"


class QueryRouter:
    """Classifies user query intent using heuristics and keywords."""

    def __init__(self) -> None:
        self._troubleshooting_keywords = {
            "why", "failed", "failure", "cause", "root cause", "broke", "stopped",
            "issue", "problem", "abnormal", "alarm",
        }
        self._status_keywords = {
            "status", "condition", "current", "health", "vibration", "temperature",
        }
        self._history_keywords = {
            "history", "past", "work order", "maintenance", "repaired", "replaced",
            "done", "previous",
        }

    def route_query(self, query: str) -> QueryIntent:
        """Determine the primary intent of the query."""
        query_lower = query.lower()

        # Simple keyword matching
        if any(kw in query_lower for kw in self._troubleshooting_keywords):
            return QueryIntent.TROUBLESHOOTING

        if any(kw in query_lower for kw in self._history_keywords):
            return QueryIntent.MAINTENANCE_HISTORY

        if any(kw in query_lower for kw in self._status_keywords):
            return QueryIntent.ASSET_STATUS

        return QueryIntent.GENERAL_KNOWLEDGE
