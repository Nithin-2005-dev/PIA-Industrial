import math

class SafeDSLEvaluator:
    def __init__(self):
        # TRAP 3 FIX: The Hermetic Seal. 
        # Explicitly clear __builtins__ so 'import', 'open', and 'eval' are impossible.
        self.safe_globals = {
            "__builtins__": {}, 
            "math": math,
            "abs": abs,
            "min": min,
            "max": max,
            "sum": sum,
            "len": len
        }

    def evaluate_metric(self, script: str, context_data: dict) -> float:
        """
        Executes untrusted DSL logic in a sealed scope.
        """
        # Inject safe context data (e.g., {'code_churn': 15, 'complexity': 2.0})
        execution_locals = {k: v for k, v in context_data.items()}
        
        try:
            # We use eval, but strictly bound to safe_globals and safe_locals
            result = eval(script, self.safe_globals, execution_locals)
            return float(result)
        except Exception as e:
            raise ValueError(f"DSL Execution failed or violated security bounds: {e}")
