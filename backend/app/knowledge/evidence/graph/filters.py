import re

class OntologicalStopWordFilter:
    """
    Prevents "God Nodes" from entering the graph.
    Config files, lockfiles, and documentation naturally attract massive numbers of 
    dependency and authored edges, but have virtually no architectural or structural value.
    """

    DEFAULT_STOP_WORDS = [
        r"^package\.json$",
        r"^yarn\.lock$",
        r"^package-lock\.json$",
        r"^.*\.lock$",
        r"^README\.md$",
        r"^\.gitignore$",
        r"^\.dockerignore$",
        r"^\.env.*",
        r"^pytest\.ini$",
        r"^tox\.ini$",
        r"^setup\.cfg$",
        r"^pyproject\.toml$",
        r"^requirements\.txt$",
    ]

    def __init__(self, patterns: list[str] | None = None):
        self._patterns = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in (patterns if patterns is not None else self.DEFAULT_STOP_WORDS)
        ]

    def should_drop(self, target_name: str) -> bool:
        """
        Returns True if the target matches any of the stop-word patterns.
        """
        for pattern in self._patterns:
            if pattern.match(target_name):
                return True
        return False
