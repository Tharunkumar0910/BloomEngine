"""
knowledge_consistency_validator.py
====================================
Evaluates academic appropriateness of extra concepts introduced by a candidate question.

Called ONLY by validation_engine.py. Never calls other validators.

Returns a (knowledge_score, details_dict) tuple.
knowledge_score is normalised to 0–10.

details_dict keys:
    extra_concepts          list[str]
    classified              dict {concept: class}
    domain_drift            bool
    drift_confidence        float
    components              dict  (internal score breakdown)
    knowledge_score         float
    validation_explanation  dict  (structured JSON with status/reason/suggestion)
"""

from typing import Optional
import config
from question_profile import QuestionProfile
from knowledge.concepts import (
    get_topic_entry,
    get_concept_weight,
    get_concept_meta,
    find_domain_for_concept,
    resolve_concept_alias,
)
from spacy_utils import get_spacy_doc, expand_abbreviations

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _normalize(text: str) -> str:
    return text.lower().strip()


def _get_lemma(token_text: str, doc) -> str:
    for token in doc:
        if token.text.lower() == token_text:
            return token.lemma_.lower()
    return token_text


def _match_concept(concept: str, target_set: set,
                   st_model=None, get_embedding_fn=None) -> bool:
    """
    Try to match concept against target_set using ordered matching:
    1. Exact  2. Lemma  3. Abbreviation  4. Synonym  5. Semantic  6. Fuzzy
    """
    c = _normalize(concept)
    if not c:
        return False

    # 1. Exact
    if c in target_set:
        return True

    # 2. Lemma
    doc_c = get_spacy_doc(c)
    lemma_c = _get_lemma(c, doc_c)
    if lemma_c in target_set:
        return True
    for t in target_set:
        doc_t = get_spacy_doc(t)
        if _get_lemma(t, doc_t) == lemma_c:
            return True

    # 3. Abbreviation expansion
    expanded = expand_abbreviations(c)
    if expanded != c:
        if expanded in target_set:
            return True
        for t in target_set:
            if _normalize(t) == expanded:
                return True

    # 4. Concept synonyms (supports both str and list values)
    syn_map = getattr(config, "CONCEPT_SYNONYMS", {})
    syn_value = syn_map.get(c)
    if syn_value is not None:
        synonyms = syn_value if isinstance(syn_value, list) else [syn_value]
        for syn in synonyms:
            syn_norm = _normalize(syn)
            if syn_norm in target_set:
                return True
            # also check reverse: any target is this synonym
            for t in target_set:
                if _normalize(t) == syn_norm:
                    return True

    # 5. Semantic similarity
    sem_threshold = getattr(config, "KNOWLEDGE_SEMANTIC_THRESHOLD", 0.55)
    if st_model is not None and get_embedding_fn is not None:
        try:
            import numpy as np
            emb_c = get_embedding_fn(c, st_model)
            for t in target_set:
                emb_t = get_embedding_fn(t, st_model)
                sim = float(np.dot(emb_c, emb_t) / (
                    (np.linalg.norm(emb_c) * np.linalg.norm(emb_t)) + 1e-9))
                if sim >= sem_threshold:
                    return True
        except Exception:
            pass

    # 6. Fuzzy (last resort)
    fuzzy_threshold = getattr(config, "KNOWLEDGE_FUZZY_THRESHOLD", 88)
    try:
        from rapidfuzz import fuzz
        for t in target_set:
            if fuzz.ratio(c, t) >= fuzzy_threshold:
                return True
    except ImportError:
        pass

    return False


def _classify_extra_concept(concept: str, orig_topic: str, orig_domain: str,
                              st_model=None, get_embedding_fn=None) -> str:
    """
    Classify extra concept into: Core | Supporting | Graph Neighbor | Different Domain | Unknown
    """
    c = _normalize(concept)
    entry = get_topic_entry(orig_topic)

    if entry:
        concepts_dict = entry.get("concepts", {})
        canonical = resolve_concept_alias(c)

        # Core (importance >= 7)
        meta = concepts_dict.get(c) or concepts_dict.get(canonical)
        if meta and meta.get("importance", 0) >= 7:
            return "Core"

        # Supporting (importance 3–6)
        if meta and 3 <= meta.get("importance", 0) < 7:
            return "Supporting"

        # Graph Neighbor (any concept in the graph edges)
        graph = entry.get("graph", {})
        all_graph_concepts: set = set()
        for _src, edges in graph.items():
            all_graph_concepts.update(edges.keys())
        if c in all_graph_concepts or canonical in all_graph_concepts:
            return "Graph Neighbor"

        # Check related topics and contexts
        related_set = set(entry.get("related_topics", []) + entry.get("contexts", []))
        if _match_concept(c, related_set, st_model, get_embedding_fn):
            return "Supporting"

    # Different Domain (matches keywords of a domain that is NOT the original)
    from knowledge.domains import get_normalized_domains
    domain_map = get_normalized_domains()
    orig_domain_lower = _normalize(orig_domain)
    concept_domain = find_domain_for_concept(c)
    if concept_domain and concept_domain != orig_domain_lower:
        return "Different Domain"
    # Scan domain map directly for keyword match
    for dom_key, kws in domain_map.items():
        if dom_key == orig_domain_lower:
            continue
        if c in kws or any(c in kw or kw in c for kw in kws if len(kw) > 3):
            return "Different Domain"

    return "Unknown"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def validate_knowledge_consistency(
    original_profile: QuestionProfile,
    candidate_profile: QuestionProfile,
    st_model=None,
    get_cached_embedding_fn=None,
) -> tuple:
    """
    Evaluate academic appropriateness of extra concepts in the candidate.

    Returns (knowledge_score: float, details: dict).
    knowledge_score is normalised 0–10.
    """
    orig_topic  = _normalize(original_profile.topic)
    orig_domain = _normalize(original_profile.domain)
    cand_domain_conf = candidate_profile.domain_confidence

    orig_concepts = {_normalize(c) for c in original_profile.concepts}
    cand_concepts = {_normalize(c) for c in candidate_profile.concepts}
    extra_concepts = list(cand_concepts - orig_concepts)

    # ── Classify each extra concept ──
    classified: dict = {}
    for concept in extra_concepts:
        cls_ = _classify_extra_concept(
            concept, orig_topic, orig_domain, st_model, get_cached_embedding_fn)
        classified[concept] = cls_

    # ── Core & Supporting preservation ──
    entry = get_topic_entry(orig_topic)
    core_total = core_preserved = supp_total = supp_preserved = 0.0
    if entry:
        concepts_dict = entry.get("concepts", {})
        for concept_key, meta in concepts_dict.items():
            imp = meta.get("importance", getattr(config, "KNOWLEDGE_DEFAULT_IMPORTANCE", 5))
            if imp >= 7:
                core_total += imp
                if _match_concept(concept_key, cand_concepts,
                                  st_model, get_cached_embedding_fn):
                    core_preserved += imp
            else:
                supp_total += imp
                if _match_concept(concept_key, cand_concepts,
                                  st_model, get_cached_embedding_fn):
                    supp_preserved += imp

    core_ratio = (core_preserved / core_total) if core_total > 0 else 1.0
    supp_ratio = (supp_preserved / supp_total) if supp_total > 0 else 1.0

    # ── Graph neighbour bonus ──
    graph = entry.get("graph", {}) if entry else {}
    all_graph_concepts: set = set()
    for _src, edges in graph.items():
        all_graph_concepts.update(edges.keys())
    neighbour_bonus = 0.0
    for concept in extra_concepts:
        c = _normalize(concept)
        if c in all_graph_concepts:
            w = max(edges.get(c, 0.0) for _src, edges in graph.items() if c in edges) if graph else 0.0
            neighbour_bonus += w * 0.1   # bonus capped per concept

    # ── Extra concept penalties (importance × factor) ──
    domain_penalty = 0.0
    unknown_penalty = 0.0
    domain_factor  = getattr(config, "DOMAIN_PENALTY_FACTOR", 0.30)
    unknown_factor = getattr(config, "UNKNOWN_PENALTY_FACTOR", 0.10)
    default_imp    = getattr(config, "KNOWLEDGE_DEFAULT_IMPORTANCE", 5)

    for concept, cls_ in classified.items():
        meta = (get_concept_meta(orig_topic, concept)
                if entry else None)
        imp = meta["importance"] if meta else default_imp
        if cls_ == "Different Domain":
            domain_penalty += imp * domain_factor
        elif cls_ == "Unknown":
            unknown_penalty += imp * unknown_factor

    # ── Intent mismatch penalty ──
    intent_penalty = 0.0
    if (original_profile.intent != candidate_profile.intent
            and candidate_profile.intent_confidence >= 0.9):
        intent_penalty = getattr(config, "INTENT_MISMATCH_PENALTY", 1.5)

    # ── Knowledge score components ──
    w_core  = getattr(config, "KNOWLEDGE_WEIGHT_CORE", 0.50)
    w_supp  = getattr(config, "KNOWLEDGE_WEIGHT_SUPPORTING", 0.30)
    w_graph = getattr(config, "KNOWLEDGE_WEIGHT_GRAPH", 0.20)

    raw_score = (
        core_ratio * w_core * 10
        + supp_ratio * w_supp * 10
        + min(neighbour_bonus, 2.0) * w_graph * 10
        - domain_penalty
        - unknown_penalty
        - intent_penalty
    )
    knowledge_score = round(max(0.0, min(10.0, raw_score)), 3)

    # ── Domain drift detection (confidence-gated) ──
    ignore_thr  = getattr(config, "VALIDATION_PROFILES", {}).get(
        getattr(config, "ACTIVE_VALIDATION_PROFILE", "balanced"), {}
    ).get("domain_confidence_ignore", 0.60)
    reject_thr  = getattr(config, "VALIDATION_PROFILES", {}).get(
        getattr(config, "ACTIVE_VALIDATION_PROFILE", "balanced"), {}
    ).get("domain_confidence_reject", 0.80)

    domain_drift = False
    drift_confidence = cand_domain_conf
    different_domain = (_normalize(candidate_profile.domain) != orig_domain)

    if different_domain:
        if cand_domain_conf >= reject_thr:
            domain_drift = True
        # below ignore_thr: skip check entirely (drift stays False)

    # ── Build structured validation explanation ──
    def _status(ok: bool) -> str:
        return "PASS" if ok else "FAIL"

    explanation: dict = {
        "Domain": {
            "status":     _status(not different_domain),
            "original":   original_profile.domain,
            "candidate":  candidate_profile.domain,
            "confidence": round(cand_domain_conf, 4),
        },
        "Topic": {
            "status":   _status(
                _normalize(original_profile.topic) == _normalize(candidate_profile.topic)
            ),
            "original":  original_profile.topic,
            "candidate": candidate_profile.topic,
        },
        "KnowledgeConsistency": {
            "status":          _status(domain_penalty == 0.0 and unknown_penalty < 1.0),
            "score":           knowledge_score,
            "core_preservation":  round(core_ratio, 4),
            "supp_preservation":  round(supp_ratio, 4),
            "extra_concepts":  len(extra_concepts),
            "classified":      classified,
        },
        "Intent": {
            "status":          _status(intent_penalty == 0.0),
            "original":        original_profile.intent,
            "candidate":       candidate_profile.intent,
            "original_conf":   round(original_profile.intent_confidence, 4),
            "candidate_conf":  round(candidate_profile.intent_confidence, 4),
            **({"reason":      "Intent shifted from '{}' to '{}'.".format(
                                original_profile.intent, candidate_profile.intent),
                "suggestion":  "FLAN may have changed the question purpose."
               } if intent_penalty > 0 else {}),
        },
        "DomainDrift": {
            "status":     _status(not domain_drift),
            "detected":   domain_drift,
            "confidence": round(drift_confidence, 4),
            **({"reason":     "Domain changed to '{}' with confidence {:.0%}.".format(
                               candidate_profile.domain, cand_domain_conf),
                "suggestion": "Candidate introduces concepts from a different domain."
               } if domain_drift else {}),
        },
    }

    # Add reason/suggestion to KnowledgeConsistency FAIL
    if explanation["KnowledgeConsistency"]["status"] == "FAIL":
        top_penalty = max(
            (c for c, cl in classified.items() if cl == "Different Domain"),
            default=None
        )
        if top_penalty:
            explanation["KnowledgeConsistency"]["reason"] = (
                f"Concept '{top_penalty}' introduces a different domain."
            )
            explanation["KnowledgeConsistency"]["suggestion"] = (
                "Remove or replace concepts that belong to a different domain."
            )

    components = {
        "core_preservation":  round(core_ratio, 4),
        "supp_preservation":  round(supp_ratio, 4),
        "graph_bonus":        round(min(neighbour_bonus, 2.0), 4),
        "domain_penalty":     round(domain_penalty, 4),
        "unknown_penalty":    round(unknown_penalty, 4),
        "intent_penalty":     round(intent_penalty, 4),
        "raw_score":          round(raw_score, 4),
    }

    details = {
        "extra_concepts":         extra_concepts,
        "classified":             classified,
        "domain_drift":           domain_drift,
        "drift_confidence":       round(drift_confidence, 4),
        "components":             components,
        "knowledge_score":        knowledge_score,
        "validation_explanation": explanation,
    }

    return knowledge_score, details
