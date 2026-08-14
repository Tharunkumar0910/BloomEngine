from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class ValidationEngineOutput:
    bloom_score: float
    concept_score: float
    entity_score: float
    number_score: float
    semantic_score: float
    duplicate_score: float
    grammar_score: float
    domain_score: float
    topic_score: float
    total_score: float
    passed: bool
    rejection_reason: str
    detailed_metrics: Dict[str, Any] = field(default_factory=dict)
    # v2.0 fields
    knowledge_score: float = 0.0
    knowledge_details: Dict[str, Any] = field(default_factory=dict)
    validation_explanation: Dict[str, Any] = field(default_factory=dict)
    domain_drift: bool = False
    generation_time_ms: float = 0.0
