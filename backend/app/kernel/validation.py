from typing import Any
from .models import CapabilityResult, CapabilityCard

class CapabilitySchemaException(Exception):
    """Raised when a CapabilityResult fails schema validation."""
    pass

class ConsistencyCheckException(Exception):
    """Raised when a CapabilityResult is internally inconsistent or missing metadata."""
    pass

class CapabilityValidator:
    """
    Validates both the structural schema and the internal consistency
    of deterministic capability outputs.
    """
    
    @classmethod
    def validate(cls, result: CapabilityResult, tool_spec: CapabilityCard) -> None:
        """
        Validates the CapabilityResult. Raises an exception if validation fails.
        """
        if result.status != "SUCCESS":
            return # Don't validate failed results
            
        cls._validate_consistency(result)
        if result.report is not None:
            cls._validate_schema(result.report, tool_spec.contract.output_type, tool_spec.name)
        
    @classmethod
    def _validate_consistency(cls, result: CapabilityResult) -> None:
        if not result.evidence_ids:
            raise ConsistencyCheckException("CapabilityResult must contain at least one evidence_id.")
            
        if not (0.0 <= result.confidence <= 1.0):
            raise ConsistencyCheckException(f"CapabilityResult confidence must be between 0.0 and 1.0. Got {result.confidence}")
            
        if not result.provenance:
            raise ConsistencyCheckException("CapabilityResult must include a provenance chain.")
            
        if not result.raw_output:
            raise ConsistencyCheckException("CapabilityResult raw_output cannot be empty.")
            
        if not result.report:
            raise ConsistencyCheckException("CapabilityResult report cannot be empty.")
            
        if not result.explanation:
            raise ConsistencyCheckException("CapabilityResult explanation cannot be empty.")

    @classmethod
    def _validate_schema(cls, output: Any, expected_type: type, tool_name: str) -> None:
        if not isinstance(output, expected_type) and expected_type is not dict:
            if hasattr(expected_type, '__name__'):
                raise CapabilitySchemaException(f"{tool_name} output must be of type {expected_type.__name__}. Got {type(output).__name__}")
            else:
                raise CapabilitySchemaException(f"{tool_name} output is not of the expected type.")
