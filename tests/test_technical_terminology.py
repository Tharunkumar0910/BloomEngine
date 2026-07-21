import pytest
import config
from knowledge.terminology import (
    TECHNICAL_TERMINOLOGY,
    get_topic_terminology,
    is_term_present_in_profile,
)
from question_profile import QuestionProfile

class DummyValidationOutput:
    def __init__(self, detailed_metrics=None, rejection_reason=""):
        self.detailed_metrics = detailed_metrics or {}
        self.rejection_reason = rejection_reason
        self.total_score = 70.0

def test_terminology_registry_structure():
    """Verify that the registry contains valid entries with required fields."""
    assert isinstance(TECHNICAL_TERMINOLOGY, dict)
    assert len(TECHNICAL_TERMINOLOGY) > 0
    for topic, data in TECHNICAL_TERMINOLOGY.items():
        assert "preferred" in data
        assert "weak" in data
        assert "minimum_preferred" in data
        assert isinstance(data["preferred"], list)
        assert isinstance(data["weak"], list)
        assert isinstance(data["minimum_preferred"], int)

def test_get_topic_terminology():
    """Verify get_topic_terminology returns correct entries and handles aliases."""
    # Canonical name
    res = get_topic_terminology("breadth first search")
    assert res is not None
    assert "graph" in res["preferred"]
    
    # Alias / acronym
    res_alias = get_topic_terminology("bfs")
    assert res_alias is not None
    assert res_alias == res
    
    # Invalid topic
    assert get_topic_terminology("unknown topic") is None

def test_is_term_present_in_profile():
    """Verify is_term_present_in_profile scans QuestionProfile fields."""
    profile = QuestionProfile(
        raw_question="Explain BFS on a graph",
        normalized_question="explain bfs on a graph",
        source_bloom="Understand",
        domain="CS",
        domain_confidence=1.0,
        topic="breadth first search",
        topic_confidence=1.0,
        concepts={"breadth first search"},
        technical_entities=("graph",),
        keywords=("bfs", "graph"),
        noun_chunks=("bfs", "graph")
    )
    
    assert is_term_present_in_profile("graph", profile) is True
    assert is_term_present_in_profile("bfs", profile) is True
    assert is_term_present_in_profile("queue", profile) is False





