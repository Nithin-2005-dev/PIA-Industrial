from typing import List
from .models import ExecutionState, Intent, CapabilityStatus

class InvariantViolation(Exception):
    pass

class InvariantChecker:
    @staticmethod
    def validate(state: ExecutionState) -> None:
        violations = []
        
        # Invariant 7: Repository queries always execute after repository loading.
        if state.classification.requires_repository and not state.prompt_context.workspace_session:
            violations.append("Invariant 7 violated: Repository loaded context missing for repository query.")
                
        if violations:
            raise InvariantViolation("\n".join(violations))
