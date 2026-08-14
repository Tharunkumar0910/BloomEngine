from dataclasses import dataclass, field
from typing import Set, Tuple, Dict, Any

@dataclass(frozen=True)
class QuestionProfile:
    raw_question: str
    normalized_question: str
    source_bloom: str
    domain: str
    domain_confidence: float
    topic: str
    topic_confidence: float
    matched_domain_keywords: Tuple[str, ...] = field(default_factory=tuple)
    matched_topic_keywords: Tuple[str, ...] = field(default_factory=tuple)
    concepts: Set[str] = field(default_factory=set)
    technical_entities: Tuple[str, ...] = field(default_factory=tuple)
    numbers: Tuple[str, ...] = field(default_factory=tuple)
    keywords: Tuple[str, ...] = field(default_factory=tuple)
    noun_chunks: Tuple[str, ...] = field(default_factory=tuple)
    dependency_tokens: Tuple[str, ...] = field(default_factory=tuple)
    # v2.0 fields — all optional with safe defaults
    intent: str = "explain"
    intent_confidence: float = 1.0
    processing_time: float = 0.0    # seconds taken to build this profile
    parse_method: str = "spacy"     # always "spacy"; diagnostic use
    profile_version: str = "2.1"
    
    # v2.1 fields
    subject: str = ""
    subject_confidence: float = 0.0
    candidate_domains: Dict[str, float] = field(default_factory=dict)
    candidate_subjects: Dict[str, float] = field(default_factory=dict)
    candidate_topics: Dict[str, float] = field(default_factory=dict)
    matched_terms: Dict[str, Tuple[str, ...]] = field(default_factory=dict)
