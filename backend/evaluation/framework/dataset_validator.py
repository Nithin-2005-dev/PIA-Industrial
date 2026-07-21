import json
from pathlib import Path
import hashlib
import logging

logger = logging.getLogger(__name__)

class DatasetValidator:
    """
    Quality gate for dataset snapshots before benchmark execution.
    Verifies checksums, required files, and parses JSON.
    """
    
    @classmethod
    def validate(cls, dataset_path: str) -> bool:
        base_dir = Path(dataset_path)
        manifest_path = base_dir / "manifest.json"
        
        if not manifest_path.exists():
            logger.error(f"Manifest not found at {manifest_path}")
            return False
            
        with open(manifest_path, "r") as f:
            try:
                manifest = json.load(f)
            except json.JSONDecodeError:
                logger.error("Failed to parse manifest.json")
                return False
                
        checksums = manifest.get("checksums", {})
        if not checksums:
            logger.error("Manifest missing 'checksums' field.")
            return False
            
        raw_dir = base_dir / "raw"
        for filename, expected_hash in checksums.items():
            filepath = raw_dir / filename
            if not filepath.exists():
                logger.error(f"Missing required file: {filename}")
                return False
                
            with open(filepath, "r") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON in {filename}")
                    return False
                    
            serialized = json.dumps(data, sort_keys=True).encode()
            actual_hash = hashlib.sha256(serialized).hexdigest()
            
            if actual_hash != expected_hash:
                logger.error(f"Checksum mismatch for {filename}. Expected: {expected_hash}, got: {actual_hash}")
                return False
                
        # Optional: Log quality metrics from manifest
        stats = manifest.get("stats", {})
        logger.info(f"Dataset Health: Commits={stats.get('commits')}, PRs={stats.get('pull_requests')}, Issues={stats.get('issues')}, Contributors={stats.get('contributors')}")
        logger.info("Dataset Integrity: PASS")
        return True
