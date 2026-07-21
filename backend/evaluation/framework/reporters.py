import json
from pathlib import Path

class JSONReporter:
    @staticmethod
    def save_results(results: dict, metadata: dict = None, output_dir: str = "evaluation/reports"):
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        
        output_payload = {
            "metadata": metadata or {},
            "results": results
        }
        
        with open(out_path / "evaluation_results.json", "w") as f:
            json.dump(output_payload, f, indent=4)
            
        history_path = Path("evaluation/history")
        history_path.mkdir(parents=True, exist_ok=True)
        from datetime import datetime, timezone
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
        with open(history_path / f"{timestamp}.json", "w") as f:
            json.dump(output_payload, f, indent=4)
            
    @staticmethod
    def save_metrics(metrics: dict, output_dir: str = "evaluation/reports"):
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        
        with open(out_path / "metrics.json", "w") as f:
            json.dump(metrics, f, indent=4)
