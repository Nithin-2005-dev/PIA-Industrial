from typing import Dict, List, Optional

class MeasurementConfig:
    def __init__(self):
        # 1. Activity Thresholds
        self.MIN_CHURN_THRESHOLD: float = 5.0
        
        # 2. Impact Depth Multipliers
        self.HIGH_RISK_DIRECTORIES = ['/core/', '/base/', '/shared/', '/infrastructure/']
        self.ROOT_FILE_MULTIPLIER = 1.5
        self.CORE_DIR_MULTIPLIER = 2.0
        
        # 3. Domain Boundaries (ERP Specific routing removed from evaluators)
        self.DOMAIN_MARKERS = {
            'admin': 'admin_dashboard',
            'client': 'client_portal',
            'vendor': 'vendor_dashboard',
            'staff': 'staff_dashboard'
        }

    def get_file_weight(self, filename: str, status: str, context: str = "general") -> float:
        """Centralized weighting logic."""
        if status == "renamed":
            return 0.0
            
        lower = filename.lower()
        if lower.endswith(('.lock', '.svg', '.png', '.min.js')):
            return 0.0
            
        if context == "impact" and lower.endswith(('.md', '.txt', '.gitignore')):
            return 0.0
        elif context == "general" and lower.endswith(('.md', '.txt', '.json', '.yaml')):
            return 0.1
            
        return 1.0

    def resolve_subsystem(self, path: str) -> str:
        """Centralized domain routing."""
        lower_path = path.lower()
        for marker, domain in self.DOMAIN_MARKERS.items():
            if marker in lower_path:
                return domain
                
        parts = path.split('/')
        if parts[0] in ['src', 'app', 'backend', 'frontend'] and len(parts) > 1:
            return f"{parts[0]}/{parts[1]}"
        return parts[0]
        
    def get_depth_multiplier(self, path: str) -> float:
        """Centralized impact multiplier."""
        lower_path = path.lower()
        if any(core_dir in lower_path for core_dir in self.HIGH_RISK_DIRECTORIES):
            return self.CORE_DIR_MULTIPLIER
            
        depth = path.count('/')
        if depth == 0: return self.ROOT_FILE_MULTIPLIER
        if depth == 1: return 1.2
        return 1.0
