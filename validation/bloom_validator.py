import string
import config

def validate_bloom_verbs(question: str, target_bloom: str) -> tuple:
    """Validate generated question against the configurable BLOOM_PROFILES.

    Returns (is_valid: bool, reason: str).
    """
    words_raw = question.split()
    if not words_raw:
        return True, "None"

    words = [
        w.translate(str.maketrans("", "", string.punctuation)).lower()
        for w in words_raw
    ]
    words = [w for w in words if w]
    if not words:
        return True, "None"

    first_word = words[0]
    sentence_set = set(words)

    all_bloom_verbs = getattr(config, "ALL_BLOOM_VERBS", set())
    if first_word in all_bloom_verbs and words[1:].count(first_word) > 0:
        return False, f"Repeated Bloom Verb: {first_word}"

    # Get profiles from config
    bloom_profiles = getattr(config, "BLOOM_PROFILES", {})
    profile = bloom_profiles.get(target_bloom)
    if profile is None:
        return True, "None"

    # Forbidden start verbs
    if first_word in profile["forbidden_start_verbs"]:
        return False, f"Wrong Start Verb: {first_word}"

    # Allowed start verbs (if configured)
    if profile["allowed_start_verbs"] is not None:
        if first_word not in profile["allowed_start_verbs"]:
            # Return relaxed pass — allowed_start_verbs is advisory only
            pass

    # Forbidden body verbs
    conflict_body = sentence_set.intersection(profile["forbidden_body_verbs"])
    if conflict_body:
        return False, f"Forbidden Word: {list(conflict_body)[0]}"

    # Evaluate-level indicators present in a lower Bloom level
    conflict_indicator = sentence_set.intersection(profile["evaluate_indicators"])
    if conflict_indicator:
        return (
            False,
            f"{target_bloom} Contains Evaluate Indicator: {list(conflict_indicator)[0]}",
        )

    return True, "None"
