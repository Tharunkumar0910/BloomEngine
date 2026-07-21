import config
from knowledge import compare_topics

def validate_topic(orig_prof, cand_prof) -> float:
    """
    Validates topic preservation between source and candidate profiles.
    Returns:
        topic_score_ratio (float)
    """
    comparison = compare_topics(orig_prof, cand_prof)
    topic_scores = getattr(config, "TOPIC_SCORE", {
        "same_topic": 1.0,
        "related_topic": 0.8,
        "same_domain": 0.4,
        "different_domain": 0.0,
    })
    return topic_scores.get(comparison, 0.0)
