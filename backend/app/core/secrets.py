import os
from abc import ABC, abstractmethod

class ISecretProvider(ABC):
    @abstractmethod
    def get_secret(self, key: str) -> str:
        """Fetch a secret securely by its key."""
        pass

class EnvironmentSecretProvider(ISecretProvider):
    def get_secret(self, key: str) -> str:
        value = os.environ.get(key)
        if not value:
            raise ValueError(f"Secret for key '{key}' not found in environment.")
        return value

class MockSecretProvider(ISecretProvider):
    def __init__(self, secrets: dict = None):
        self.secrets = secrets or {}
        
    def get_secret(self, key: str) -> str:
        return self.secrets.get(key, "mock_token_123")
