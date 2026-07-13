import re
import config
import torch
from spacy_utils import get_spacy_doc, expand_abbreviations

def detect_entities(text) -> set:
    """Detect technical entities like DBMS, SQL, TCP, MongoDB, Python, etc. using dictionary, spaCy & patterns."""
    if hasattr(text, "_entities") and text._entities is not None:
        return text._entities

    if isinstance(text, str):
        doc = get_spacy_doc(text)
        text_str = text
    elif hasattr(text, "doc"):  # NLPContext
        doc = text.doc
        text_str = text.text
    else:  # spacy Doc
        doc = text
        text_str = doc.text

    entities = set()
    
    # 1. Dictionary matching (case-insensitive)
    text_lower = text_str.lower()
    tech_dict = getattr(config, "TECH_ENTITY_DICTIONARY", [])
    for term in tech_dict:
        term_lower = term.lower()
        if "+" in term_lower or "#" in term_lower or "." in term_lower:
            if term_lower in text_lower:
                entities.add(term_lower)
        else:
            pattern = r'\b' + re.escape(term_lower) + r'\b'
            if re.search(pattern, text_lower):
                entities.add(term_lower)
                
    # 2. Regex patterns for uppercase acronyms, camelCase, languages/frameworks
    acronym_pattern = re.compile(r'\b[A-Z0-9]{2,}\b|\b[A-Z][a-z]+[A-Z][a-zA-Z0-9]*\b')
    hyphen_pattern = re.compile(r'\b[a-zA-Z0-9]+[-+][a-zA-Z0-9+-]+\b')
    lang_pattern = re.compile(r'\bC\+\+|\bC#\b|\b\.NET\b', re.IGNORECASE)
    
    for word in text_str.split():
        w_clean = word.strip(".,?!():;\"'")
        if acronym_pattern.match(w_clean) or hyphen_pattern.match(w_clean) or lang_pattern.match(w_clean):
            entities.add(w_clean.lower())
            
    # 3. Named entities from spaCy
    for ent in doc.ents:
        if ent.label_ in ("ORG", "PRODUCT", "LAW", "WORK_OF_ART"):
            entities.add(ent.text.lower().strip())
            
    # 4. Proper nouns from spaCy
    for token in doc:
        if token.pos_ == "PROPN" and not token.is_stop:
            entities.add(token.text.lower().strip())
            
    # Read ignore list from config
    generic_ignore = getattr(config, "ENTITY_IGNORE_WORDS", set())
    entities = {e for e in entities if e not in generic_ignore and len(e) > 1}
    return entities

def is_entity_present(entity: str, cand_entities: set, cand_text: str, st_model=None, get_cached_embedding_fn=None) -> bool:
    """Helper to check if a specific entity (or abbreviation or semantic equivalent) exists in candidate."""
    if entity in cand_entities:
        return True
    norm_ent = expand_abbreviations(entity)
    norm_cand = expand_abbreviations(cand_text.lower())
    if norm_ent in norm_cand:
        return True
    if st_model and get_cached_embedding_fn:
        emb_ent = get_cached_embedding_fn(entity, st_model)
        for ce in cand_entities:
            emb_ce = get_cached_embedding_fn(ce, st_model)
            import torch
            with torch.inference_mode():
                sim = float(torch.nn.functional.cosine_similarity(emb_ent.unsqueeze(0), emb_ce.unsqueeze(0)).item())
            entity_sim_threshold = getattr(config, "ENTITY_SIMILARITY_THRESHOLD", 0.90)
            if sim >= entity_sim_threshold:
                return True
    return False

def validate_entities(original_q, candidate_q, st_model=None, get_cached_embedding_fn=None) -> tuple:
    """
    Validates technical entity preservation and penalizes unrelated additions.
    Embeddings for all original and candidate entities are precomputed once
    (O(N+M)) and reused throughout, avoiding redundant SentenceTransformer calls.
    Returns: (score, details_dict)
    """
    if hasattr(original_q, "entities"):  # NLPContext
        orig_ctx = original_q
        orig_entities = orig_ctx.entities
        original_text = orig_ctx.text
    else:
        orig_ctx = original_q
        orig_entities = detect_entities(original_q)
        original_text = original_q

    if hasattr(candidate_q, "entities"):  # NLPContext
        cand_ctx = candidate_q
        cand_entities = cand_ctx.entities
        candidate_text = cand_ctx.text
    else:
        cand_ctx = candidate_q
        cand_entities = detect_entities(candidate_q)
        candidate_text = candidate_q

    entity_score_max = getattr(config, "ENTITY_SCORE", 15.0)
    entity_penalty_val = getattr(config, "ENTITY_PENALTY", 0.2)
    entity_related_threshold = getattr(config, "ENTITY_RELATED_THRESHOLD", 0.60)

    # Extract comparison texts (original entities + concepts)
    orig_concepts = orig_ctx.concepts if hasattr(orig_ctx, "concepts") else None
    if orig_concepts is None:
        from concept_validator import extract_concepts
        orig_concepts = extract_concepts(orig_ctx)

    comparison_texts = list(orig_entities) + list(orig_concepts)

    # ── Precompute all embeddings in one pass ──────────────────────────────
    # orig entity embeddings
    orig_emb_map = {}
    if st_model and get_cached_embedding_fn:
        for e in orig_entities:
            orig_emb_map[e] = get_cached_embedding_fn(e, st_model)

    # candidate entity embeddings
    cand_emb_map = {}
    if st_model and get_cached_embedding_fn:
        for e in cand_entities:
            cand_emb_map[e] = get_cached_embedding_fn(e, st_model)

    # comparison text embeddings (orig entities + orig concepts)
    comp_emb_list = []
    if st_model and get_cached_embedding_fn and comparison_texts:
        for comp_txt in comparison_texts:
            comp_emb_list.append(get_cached_embedding_fn(comp_txt, st_model))

    # ── Helper: check if entity is present in candidate (uses precomputed embs) ──
    def _is_present(entity: str) -> bool:
        if entity in cand_entities:
            return True
        norm_ent = expand_abbreviations(entity)
        norm_cand = expand_abbreviations(candidate_text.lower())
        if norm_ent in norm_cand:
            return True
        if orig_emb_map and cand_emb_map:
            emb_ent = orig_emb_map.get(entity)
            if emb_ent is None:
                emb_ent = get_cached_embedding_fn(entity, st_model)
            entity_sim_threshold = getattr(config, "ENTITY_SIMILARITY_THRESHOLD", 0.90)
            for ce, emb_ce in cand_emb_map.items():
                with torch.inference_mode():
                    sim = float(torch.nn.functional.cosine_similarity(
                        emb_ent.unsqueeze(0), emb_ce.unsqueeze(0)).item())
                if sim >= entity_sim_threshold:
                    return True
        return False

    # ── Helper: check if a candidate entity is related to the original context ──
    def _is_related(c_ent: str) -> bool:
        c_ent_expanded = expand_abbreviations(c_ent)
        for comp_txt in comparison_texts:
            if c_ent == comp_txt or c_ent_expanded == expand_abbreviations(comp_txt):
                return True
        if comp_emb_list and st_model and get_cached_embedding_fn:
            emb_c = cand_emb_map.get(c_ent)
            if emb_c is None:
                emb_c = get_cached_embedding_fn(c_ent, st_model)
            for emb_comp in comp_emb_list:
                with torch.inference_mode():
                    sim = float(torch.nn.functional.cosine_similarity(
                        emb_c.unsqueeze(0), emb_comp.unsqueeze(0)).item())
                if sim >= entity_related_threshold:
                    return True
        return False

    if not orig_entities:
        unrelated_penalized = [c for c in cand_entities if not _is_related(c)]
        unrelated_penalty = entity_penalty_val * len(unrelated_penalized)
        final_ratio = max(0.0, 1.0 - unrelated_penalty)
        score = round(entity_score_max * final_ratio, 2)

        return score, {
            "preservation_ratio": 1.0,
            "original_entities": [],
            "candidate_entities": list(cand_entities),
            "preserved_entities": [],
            "missing_entities": [],
            "unrelated_entities": list(cand_entities),
            "unrelated_penalized": unrelated_penalized,
            "unrelated_penalty": unrelated_penalty
        }

    preserved = [e for e in orig_entities if _is_present(e)]
    missing = [e for e in orig_entities if e not in preserved]
    preservation_ratio = len(preserved) / len(orig_entities)

    # Identify unrelated candidate entities then filter by relatedness
    unrelated = [
        c for c in cand_entities
        if not any(c == o or expand_abbreviations(c) == expand_abbreviations(o)
                   for o in orig_entities)
    ]
    unrelated_penalized = [c for c in unrelated if not _is_related(c)]

    unrelated_penalty = entity_penalty_val * len(unrelated_penalized)
    final_ratio = max(0.0, preservation_ratio - unrelated_penalty)
    score = round(entity_score_max * final_ratio, 2)

    return score, {
        "preservation_ratio": preservation_ratio,
        "original_entities": list(orig_entities),
        "candidate_entities": list(cand_entities),
        "preserved_entities": preserved,
        "missing_entities": missing,
        "unrelated_entities": unrelated,
        "unrelated_penalized": unrelated_penalized,
        "unrelated_penalty": unrelated_penalty
    }

