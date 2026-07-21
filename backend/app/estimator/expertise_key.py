from dataclasses import dataclass


@dataclass(frozen=True)
class ExpertiseKey:
    developer_id: str
    module_id: str