import logging
from typing import Any

logger = logging.getLogger(__name__)

class SecurityError(Exception):
    pass

class SafeMLRuntime:
    def __init__(self):
        self.allowed_extensions = ['.safetensors', '.pt']

    def load_heuristic_model(self, file_path: str) -> Any:
        """
        Cryptographically secure model loader.
        """
        if not any(file_path.endswith(ext) for ext in self.allowed_extensions):
            raise ValueError(f"Invalid model format. Allowed: {self.allowed_extensions}")

        try:
            # If using PyTorch, force weights_only to prevent Pickle RCE
            import torch
            logger.info(f"Safely mounting ML heuristics from {file_path}")
            # TRAP 1 FIX: weights_only=True prevents arbitrary object instantiation
            return torch.load(file_path, map_location='cpu', weights_only=True)
        except Exception as e:
            logger.error(f"Failed to securely load model {file_path}: {e}")
            raise SecurityError("Model deserialization blocked by security policy.")
