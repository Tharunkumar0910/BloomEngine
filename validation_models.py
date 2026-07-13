from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class ValidationEngineOutput:
    bloom_score: float
    concept_score: float
    entity_score: float
    number_score: float
    semantic_score: float
    duplicate_score: float
    grammar_score: float
    total_score: float
    passed: bool
    rejection_reason: str
    detailed_metrics: Dict[str, Any] = field(default_factory=dict)
