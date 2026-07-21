"""
Prompt templates for BloomAI Arena v2.1.
Supports the flan_t5_model (new model) with Mode E (Multi-Candidate Ranking).
"""

def build_prompt(
    question: str,
    source_bloom: str,
    target_bloom: str,
    domain: str,
    topic: str,
    topic_context: str = None,
) -> str:
    """Build the standard inference prompt matching the training prompt exactly, optionally with academic context."""
    topic_str = f"\n{topic}\n\n{topic_context}" if topic_context else f" {topic}"
    return (
        "Rewrite the given university examination question from the source Bloom's Taxonomy level "
        "to the target Bloom's Taxonomy level while preserving the original concept, topic, "
        "and academic meaning. Return only the rewritten question.\n\n"
        f"Source Bloom: {source_bloom}\n"
        f"Target Bloom: {target_bloom}\n"
        f"Domain: {domain}\n"
        f"Topic:{topic_str}\n"
        f"Question: {question}"
    )

