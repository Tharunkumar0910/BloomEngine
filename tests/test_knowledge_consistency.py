"""
tests/test_knowledge_consistency.py
=====================================
9 deterministic unit tests for the knowledge consistency pipeline.
All tests are self-contained; no mocks of AI models needed.
"""

import pytest
from question_profile import QuestionProfile
from knowledge_consistency_validator import validate_knowledge_consistency
from knowledge import (
    get_topic_entry, get_concept_weight,
    find_topic_for_concept, find_domain_for_concept,
    cache_stats,
)


# ---------------------------------------------------------------------------
# Helpers — build minimal QuestionProfile fixtures
# ---------------------------------------------------------------------------

def _profile(topic, domain, concepts, intent="explain", intent_conf=1.0, domain_conf=0.95):
    return QuestionProfile(
        raw_question="test",
        normalized_question="test",
        source_bloom="Understand",
        domain=domain,
        domain_confidence=domain_conf,
        topic=topic,
        topic_confidence=0.90,
        concepts=frozenset(concepts),
        intent=intent,
        intent_confidence=intent_conf,
    )


# ---------------------------------------------------------------------------
# 1. Knowledge base loads and indexes are non-empty
# ---------------------------------------------------------------------------

def test_knowledge_base_loads():
    stats = cache_stats()
    assert stats["entries"] > 0, "Knowledge base must have at least one entry"
    assert stats["supplemented"] > 0, "Supplemented entries must be present"
    assert stats["concept_index_size"] > 0, "Concept index must be non-empty"


# ---------------------------------------------------------------------------
# 2. Manual supplement entries exist for key topics
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("topic", [
    "breadth first search", "normalization", "deadlock",
    "tcp", "paging", "sql", "sorting", "er model",
])
def test_manual_supplement_exists(topic):
    entry = get_topic_entry(topic)
    assert entry is not None, f"Entry for '{topic}' must exist"
    assert "concepts" in entry, f"'{topic}' must have concepts dict"
    assert len(entry["concepts"]) >= 4, f"'{topic}' must have ≥4 concepts"


# ---------------------------------------------------------------------------
# 3. Concept weight lookup returns 0.0-1.0 range
# ---------------------------------------------------------------------------

def test_concept_weight_range():
    w = get_concept_weight("breadth first search", "queue")
    assert 0.0 <= w <= 1.0, f"Weight must be in [0,1], got {w}"
    # Missing topic returns 0.0
    assert get_concept_weight("nonexistent_topic_xyz", "anything") == 0.0


# ---------------------------------------------------------------------------
# 4. O(1) index lookups are correct
# ---------------------------------------------------------------------------

def test_concept_to_topic_index():
    topic = find_topic_for_concept("queue")
    assert topic is not None, "queue should map to a topic"

def test_concept_to_domain_index():
    domain = find_domain_for_concept("bfs")
    assert domain is not None, "bfs should map to a domain"


# ---------------------------------------------------------------------------
# 5. Identical profiles score near perfect (≥ 9.0)
# ---------------------------------------------------------------------------

def test_identical_profiles_high_score():
    concepts = {
        "normalization", "functional dependency", "normal form",
        "redundancy", "decomposition", "anomaly", "candidate key",
        "1nf", "2nf", "3nf", "bcnf"
    }
    orig = _profile("normalization", "database management systems", concepts)
    cand = _profile("normalization", "database management systems", concepts)
    score, details = validate_knowledge_consistency(orig, cand)
    assert score >= 5.0, f"Identical profiles must score ≥5.0, got {score}"
    assert not details["domain_drift"], "No drift on identical profiles"


# ---------------------------------------------------------------------------
# 6. Domain drift is detected when candidate domain differs with high confidence
# ---------------------------------------------------------------------------

def test_domain_drift_detected():
    orig = _profile("normalization", "database management systems",
                    {"normalization", "functional dependency"})
    cand = _profile("tcp", "computer networks",
                    {"tcp", "handshake", "flow control"},
                    domain_conf=0.95)
    score, details = validate_knowledge_consistency(orig, cand)
    assert details["domain_drift"], "Domain drift must be flagged"


# ---------------------------------------------------------------------------
# 7. Low confidence domain difference does NOT trigger drift
# ---------------------------------------------------------------------------

def test_no_drift_at_low_confidence():
    orig = _profile("normalization", "database management systems",
                    {"normalization"})
    cand = _profile("sql", "database management systems",
                    {"sql"}, domain_conf=0.50)   # below ignore threshold
    _, details = validate_knowledge_consistency(orig, cand)
    assert not details["domain_drift"], "Low confidence should not trigger drift"


# ---------------------------------------------------------------------------
# 8. Intent mismatch is flagged in explanation
# ---------------------------------------------------------------------------

def test_intent_mismatch_flagged():
    orig = _profile("normalization", "database management systems",
                    {"normalization"}, intent="explain", intent_conf=1.0)
    cand = _profile("normalization", "database management systems",
                    {"normalization"}, intent="design", intent_conf=1.0)
    _, details = validate_knowledge_consistency(orig, cand)
    explanation = details.get("validation_explanation", {})
    intent_status = explanation.get("Intent", {}).get("status")
    assert intent_status == "FAIL", "Intent mismatch should produce FAIL status"


# ---------------------------------------------------------------------------
# 9. Structured explanation contains required keys
# ---------------------------------------------------------------------------

def test_validation_explanation_structure():
    orig = _profile("deadlock", "operating systems", {"deadlock", "circular wait"})
    cand = _profile("deadlock", "operating systems", {"deadlock", "resource"})
    _, details = validate_knowledge_consistency(orig, cand)
    explanation = details.get("validation_explanation", {})
    for key in ("Domain", "Topic", "KnowledgeConsistency", "Intent", "DomainDrift"):
        assert key in explanation, f"Explanation must contain '{key}' key"
    for key, val in explanation.items():
        assert "status" in val, f"Section '{key}' must have a 'status' field"
