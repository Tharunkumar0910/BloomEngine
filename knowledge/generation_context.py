from knowledge.concepts import get_topic_entry, are_equivalent

GENERIC_CONCEPTS = {
    "algorithm", "problem", "method", "system", "data", "process", "science", 
    "concept", "approach", "technique", "theory", "structure", "structures",
    "design", "implementation", "level", "analysis", "case", "study", "general",
    "introduction", "basic", "basics", "advanced", "fundamental", "fundamentals",
    "model"
}

def get_topic_concepts(topic: str) -> list:
    """
    Retrieve concepts/entities associated with this topic.
    Rank by importance descending.
    Filter out generic concept terms.
    Never inject the topic itself or its equivalent aliases.
    """
    if not topic:
        return []
        
    entry = get_topic_entry(topic)
    if not entry:
        return []
        
    concepts_dict = entry.get("concepts", {})
    if not concepts_dict:
        return []
        
    # Rank by importance descending, then alphabetically for determinism
    sorted_items = sorted(
        concepts_dict.items(),
        key=lambda x: (-x[1].get("importance", 5), x[0])
    )
    
    filtered_concepts = []
    current_tokens = 0
    token_limit = 50
    topic_clean = topic.strip().lower()
    
    for name, meta in sorted_items:
        name_clean = name.strip().lower()
        
        # Skip generic terms
        if name_clean in GENERIC_CONCEPTS:
            continue
            
        # Never inject the topic itself or its equivalent aliases
        if are_equivalent(name_clean, topic_clean):
            continue
            
        # Count words as a safe approximation for token limit
        words = name_clean.split()
        num_tokens = len(words)
        
        if current_tokens + num_tokens > token_limit:
            break
            
        filtered_concepts.append(name_clean)
        current_tokens += num_tokens
        
        if len(filtered_concepts) >= 4:
            break
            
    return filtered_concepts


def get_topic_context(topic: str) -> str:
    """
    Builds the academic context string for the prompt using positive guidance and strict limits.
    """
    # Try getting the simplified concepts from terminology first
    from knowledge.terminology import get_topic_terminology
    concepts = get_topic_terminology(topic)
    
    # Fallback to general concept knowledge if terminology is empty
    if not concepts:
        concepts = get_topic_concepts(topic)
        
    if not concepts:
        return ""
        
    lines = ["Academic Context", ""]
    for c in concepts:
        lines.append(c)
    lines.append("")
    lines.append("Use these concepts if needed.")
    
    if len(lines) > 6:
        lines = [l for l in lines if l != ""]
        if len(lines) > 6:
            lines = lines[:5] + [lines[-1]]
            
    return "\n".join(lines)
