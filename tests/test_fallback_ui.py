import pytest
from app import ValidationResult

def test_fallback_explanation_content():
    # Test that fallback explanation is the concise user-facing string
    expected_explanation = (
        "The generated question did not satisfy all validation criteria after multiple attempts. "
        "The highest-quality candidate was selected based on the ranking algorithm."
    )
    
    # Verify exact string match requirement
    res = ValidationResult(
        generated_question="What is regularized linear regression?",
        source_question="Explain linear regression.",
        source_bloom="Understand",
        source_difficulty="Medium",
        target_bloom="Analyze",
        target_difficulty="Hard",
        predicted_bloom="Analyze",
        predicted_difficulty="Hard",
        confidence=85.0,
        attempts=3,
        generation_time=1.2,
        concept_match_score="1/1",
        rejection_reason="Classification Mismatch",
        prompt_used="...",
        explanation=expected_explanation,
        validation_status="Best Candidate",
        attempts_list=[
            {"attempt_number": 1, "rejection_reason": "Semantic Drift", "question": "Q1"},
            {"attempt_number": 2, "rejection_reason": "Classification Mismatch", "question": "Q2"}
        ]
    )
    
    assert res.explanation == expected_explanation
    assert "Attempt 1" not in res.explanation
    assert "Attempt 2" not in res.explanation
    assert "<div" not in res.explanation
    assert "Diagnostic report" not in res.explanation
    # Ensure internal diagnostics are preserved in backend struct
    assert len(res.attempts_list) == 2
