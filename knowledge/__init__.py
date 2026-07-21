from typing import Optional, List
from knowledge.domains import (
    NORMALIZED_DOMAIN_MAP,
    get_normalized_domains
)
from knowledge.topics import TOPIC_MAP
from knowledge.concepts import (
    Concept,
    normalize_concept,
    canonicalize_concept_list,
    are_equivalent,
    get_equivalent_terms,
    detect_duplicate_equivalent_terms,
    get_topic_entry,
    get_concept_weight,
    get_concept_graph,
    get_concept_meta,
    resolve_concept_alias,
    find_topic_for_concept,
    find_domain_for_concept,
    get_related_topics,
    cache_stats,
    compare_topics
)
from knowledge.terminology import get_topic_terminology
from knowledge.hierarchy import (
    DOMAIN_HIERARCHY,
    DOMAIN_INDEX,
    SUBJECT_INDEX,
    TOPIC_INDEX,
    ALIAS_INDEX,
    ENTITY_INDEX,
    PHRASE_INDEX,
    KEYWORD_INDEX,
    VERB_INDEX,
    LOOKUP
)
from knowledge.generation_context import get_topic_context

def get_profile(question: str, source_bloom: Optional[str] = None):
    """
    Core entrypoint: obtains a QuestionProfile for a given input question.
    """
    from question_understanding import QuestionUnderstandingEngine
    return QuestionUnderstandingEngine.build_profile(question, source_bloom)

def lookup(term: str) -> List[dict]:
    """
    Unified lookup: queries the compiled LOOKUP index for matching domains,
    subjects, topics, concepts, entities, and keywords.
    """
    if not term:
        return []
    term_normalized = term.strip().lower()
    return LOOKUP.get(term_normalized, [])

def normalize(term: str) -> str:
    """
    Centralized normalizer mapping variations/synonyms/abbreviations to their canonical form.
    """
    return normalize_concept(term)
