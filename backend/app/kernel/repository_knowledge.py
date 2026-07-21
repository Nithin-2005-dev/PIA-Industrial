from typing import Dict, List, Any
from .adapter import PlatformResultAdapter

class RepositoryIndex:
    """Provides indexed views over the deterministic repository facts."""
    def __init__(self, adapter: PlatformResultAdapter):
        self.adapter = adapter
        self._build_indexes()

    def _build_indexes(self):
        # In a real M58 implementation, this parses the platform observations 
        # (files, packages, developers, symbols) into fast searchable dictionaries.
        # For M57.15, we'll implement a lightweight structure.
        self.files: List[str] = []
        self.directories: List[str] = []
        self.packages: List[str] = []
        self.symbols: List[str] = []
        self.developers: List[str] = []
        self.subsystems: List[str] = []
        
        try:
            # Attempt to extract developers from top_contributors
            tc = self.adapter.top_contributors()
            if "contributors" in tc:
                self.developers = [c["name"] for c in tc["contributors"]]
        except Exception:
            pass

class RepositoryKnowledge:
    """
    The semantic brain of the system.
    Wraps the raw PlatformResultAdapter and exposes high-level semantic insights
    and the searchable RepositoryIndex.
    """
    def __init__(self, adapter: PlatformResultAdapter):
        self.adapter = adapter
        self.index = RepositoryIndex(adapter)

    def get_architecture_summary(self) -> str:
        return "Deterministic architecture summary from platform."

    def get_subsystems(self) -> List[str]:
        return self.index.subsystems

    def get_developers(self) -> List[str]:
        return self.index.developers

    def search_entities(self, query: str, entity_type: str) -> List[str]:
        """Fuzzy search against the entity index."""
        # Simple substring match for M57.15
        results = []
        if entity_type.lower() in ("person", "developer"):
            results = [d for d in self.index.developers if query.lower() in d.lower()]
        elif entity_type.lower() in ("module", "package", "file", "directory"):
            # Dummy search logic for other types
            results = [query.lower()]
        return results if results else [query.lower()]
