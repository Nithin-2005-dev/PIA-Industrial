import multiprocessing
import logging

logger = logging.getLogger(__name__)

def _isolated_worker(script: str, context_data: dict, return_dict: dict):
    """Function that runs inside the isolated hardware process."""
    try:
        from app.intelligence.measurement.plugins_runtime.dsl import SafeDSLEvaluator
        evaluator = SafeDSLEvaluator()
        return_dict['result'] = evaluator.evaluate_metric(script, context_data)
    except Exception as e:
        return_dict['error'] = str(e)

class PluginEngine:
    EXECUTION_TIMEOUT_SECONDS = 2.0  # TRAP 2 FIX: Strict Halting Limit

    def execute_untrusted_plugin(self, script: str, context_data: dict) -> float:
        """
        Spawns a highly restricted sub-process to execute custom logic.
        """
        manager = multiprocessing.Manager()
        return_dict = manager.dict()
        
        # Spawn isolated process
        p = multiprocessing.Process(target=_isolated_worker, args=(script, context_data, return_dict))
        p.start()
        
        # Enforce strict timeout
        p.join(self.EXECUTION_TIMEOUT_SECONDS)
        
        if p.is_alive():
            logger.error("Plugin violated execution timeout. Terminating hardware process.")
            p.terminate()
            p.join()
            raise TimeoutError("Plugin execution exceeded maximum allowed time.")
            
        if 'error' in return_dict:
            raise RuntimeError(return_dict['error'])
            
        return return_dict.get('result', 0.0)
