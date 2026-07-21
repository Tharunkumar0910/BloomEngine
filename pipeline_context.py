from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from question_profile import QuestionProfile
from validation_models import ValidationEngineOutput

@dataclass
class PipelineContext:
    source_question: str
    source_bloom: str
    target_bloom: str
    target_difficulty: str
    source_profile: Optional[QuestionProfile] = None
    generated_candidates: List[str] = field(default_factory=list)
    candidate_profiles: List[QuestionProfile] = field(default_factory=list)
    validation_results: List[ValidationEngineOutput] = field(default_factory=list)
    best_candidate: Optional[str] = None
    timings: Dict[str, float] = field(default_factory=dict)
