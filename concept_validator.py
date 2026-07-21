import re
import config
from spacy_utils import get_spacy_doc, expand_abbreviations

def clean_concept_text(c_text: str) -> str:
    # Strip any leading/trailing non-alphanumeric character (e.g. quotes, commas, question marks)
    # but keep standard characters like +, #, - inside the word
    cleaned = re.sub(r'^[^\w+#.-]+|[^\w+#.-]+$', '', c_text).strip()
    # Collapse multiple spaces
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned

def extract_concepts_with_compounds(text) -> tuple:
    """
    Extracts key academic concepts and identifies compound noun phrases using spaCy.
    Supports raw text string, spaCy Doc, or NLPContext.
    Returns: (all_concepts: set, compound_concepts: set)
    """
    if hasattr(text, "_concepts") and text._concepts is not None:
        return text._concepts, text._compounds

    if isinstance(text, str):
        doc = get_spacy_doc(text)
    elif hasattr(text, "doc"):  # NLPContext
        doc = text.doc
    else:
        doc = text
        
    raw_concepts = set()
    
    # 1. Extract Compound phrases using dependency parsing
    for token in doc:
        if token.pos_ in ("NOUN", "PROPN") and token.dep_ != "compound":
            # Traverse descendants to collect compound modifiers
            def get_compounds(t):
                res = []
                for child in t.children:
                    if child.dep_ == "compound":
                        res.append(child)
                        res.extend(get_compounds(child))
                return res
            
            descendants = get_compounds(token)
            if descendants:
                descendants.append(token)
                descendants.sort(key=lambda t: t.i)
                phrase = " ".join([t.text.lower() for t in descendants if not t.is_stop and not t.is_punct and t.pos_ not in ("PUNCT", "SYM", "SPACE")])
                cleaned = clean_concept_text(phrase)
                if len(cleaned) > 1:
                    raw_concepts.add(cleaned)

    # 2. Extract noun chunks and clean them
    for chunk in doc.noun_chunks:
        words = [t.text.lower() for t in chunk if not t.is_stop and t.pos_ not in ("DET", "PRON", "PUNCT", "SYM", "SPACE") and not t.is_punct]
        clean_chunk = clean_concept_text(" ".join(words))
        if len(clean_chunk) > 1:
            raw_concepts.add(clean_chunk)
            
    # 3. Extract Named Entities
    for ent in doc.ents:
        words = [t.text.lower() for t in ent if not t.is_stop and t.pos_ not in ("DET", "PRON", "PUNCT", "SYM", "SPACE") and not t.is_punct]
        ent_text = clean_concept_text(" ".join(words))
        if len(ent_text) > 1:
            raw_concepts.add(ent_text)

    # 4. Extract Technical Entities from dictionary/detector
    try:
        from entity_validator import detect_entities
        tech_entities = detect_entities(doc)
        for te in tech_entities:
            te_text = clean_concept_text(te.lower())
            if len(te_text) > 1:
                raw_concepts.add(te_text)
    except Exception:
        pass

    # 5. Extract Dependency Heads (single nouns, proper nouns, and key verbs)
    for token in doc:
        if token.pos_ in ("NOUN", "PROPN", "VERB") and not token.is_stop and not token.is_punct and token.pos_ not in ("PUNCT", "SYM", "SPACE"):
            token_text = clean_concept_text(token.text.lower())
            if len(token_text) > 1:
                raw_concepts.add(token_text)
            
    # Read ignore list from config
    ignore_words = getattr(config, "CONCEPT_IGNORE_WORDS", set())

    # Define ignore sets
    ACADEMIC_VERBS = {
        "define", "list", "state", "recall", "name", "identify", "mention",
        "label", "what", "which", "explain", "describe", "summarize",
        "interpret", "discuss", "apply", "implement", "use", "demonstrate",
        "solve", "calculate", "execute", "illustrate", "analyze", "compare",
        "differentiate", "examine", "contrast", "distinguish", "appraise",
        "test", "experiment", "question", "evaluate", "assess", "critique",
        "justify", "judge", "recommend", "design", "develop", "construct",
        "formulate", "propose", "create", "make", "build", "write", "suggest",
        "retrieve", "find", "locate", "recognize", "classify", "translate",
        "rephrase", "outline", "compute", "operate", "prepare", "select",
        "criticize", "deconstruct", "attribute", "defend", "support", "rate",
        "choose", "compose", "plan", "generate", "devise", "assemble", "show",
        "provide", "provides", "provided", "shows", "shown", "determines"
    }

    EXTRA_ACADEMIC_WORDS = {
        "role", "purpose", "concept", "scenario", "context", "approach",
        "method", "system", "difference", "comparison", "relationship",
        "process", "technique", "techniques", "advantage", "advantages",
        "disadvantage", "disadvantages", "benefit", "benefits", "challenge",
        "challenges", "limitation", "limitations", "drawback", "drawbacks",
        "tradeoff", "trade-off", "tradeoffs", "trade-offs", "feature", "features",
        "aspect", "aspects", "efficiency", "performance", "suitability",
        "effectiveness", "example", "examples", "program", "code", "theory",
        "following", "term", "type", "class", "function", "value",
        "implementation", "need", "reason", "step", "way", "question", "questions",
        "answer", "answers", "problem", "problems", "solution", "solutions",
        "given", "correct", "correctly", "incorrect", "incorrectly", "appropriate",
        "scenarios", "study", "case", "based"
    }

    all_ignores = ACADEMIC_VERBS | EXTRA_ACADEMIC_WORDS | {w.lower() for w in ignore_words}

    def _get_lemma(word: str) -> str:
        word_lower = word.lower()
        for token in doc:
            if token.text.lower() == word_lower:
                return token.lemma_.lower()
        try:
            sub_doc = get_spacy_doc(word_lower)
            if len(sub_doc) > 0:
                return sub_doc[0].lemma_.lower()
        except Exception:
            pass
        return word_lower

    filtered_concepts = set()
    for c in raw_concepts:
        c_clean = c.strip().lower()
        if not c_clean:
            continue
        if " " not in c_clean:
            lemma = _get_lemma(c_clean)
            if c_clean in all_ignores or lemma in all_ignores:
                continue
            filtered_concepts.add(c_clean)
        else:
            words = c_clean.split()
            filtered_words = []
            for w in words:
                w_lemma = _get_lemma(w)
                if w not in all_ignores and w_lemma not in all_ignores and len(w) > 1:
                    filtered_words.append(w)
            cleaned = " ".join(filtered_words).strip()
            if len(cleaned) > 1:
                filtered_concepts.add(cleaned)

    raw_concepts = filtered_concepts

    
    # ISSUE 1 FIX: Remove only exact duplicates, NOT substring-covered concepts.
    # Keeping both "database" and "database management system" is intentional —
    # generated questions often preserve the root word without the full compound.
    from knowledge.concepts import Concept, normalize_concept
    concepts = {Concept(c, normalize_concept(c)) for c in raw_concepts}
    
    # Classify compound concepts as those containing a space
    compound_concepts = {c for c in concepts if " " in c}
    
    return concepts, compound_concepts

def extract_concepts(text) -> set:
    """Extract key academic concepts from a question (backward compatibility)."""
    if hasattr(text, "concepts"):
        return text.concepts
    concepts, _ = extract_concepts_with_compounds(text)
    return concepts

def check_concept_match(
    concept: str,
    cand_text,
    cand_doc,
    st_model=None,
    get_cached_embedding_fn=None,
    cand_concepts_precomputed=None,
    cand_compounds_precomputed=None,
) -> tuple:
    """
    Check if a concept matches in the candidate text.
    Matching order (Issue 3):
      1. Exact Match
      2. Abbreviation Expansion
      3. Concept Synonyms
      4. Phrase Similarity  ← moved before Lemma Match
      5. Lemma Match
      6. Semantic Similarity
      7. No Match

    cand_concepts_precomputed / cand_compounds_precomputed: pre-extracted candidate
    concepts passed in to avoid repeated extraction inside loops (Issue 4).
    Returns: (matched: bool, method: str, similarity_score: float)
    """
    if hasattr(cand_text, "text"):  # NLPContext
        cand_ctx = cand_text
        cand_text = cand_ctx.text
        cand_doc = cand_ctx.doc

    concept_lower = concept.lower()
    cand_lower = cand_text.lower()
    
    # 0. Canonical Comparison
    from knowledge.concepts import are_equivalent, get_equivalent_terms, normalize_concept
    concept_canon = normalize_concept(concept_lower)
    
    # Check if candidate's precomputed concepts contains any canonically equivalent concept
    if cand_concepts_precomputed is not None:
        for cc in cand_concepts_precomputed:
            if are_equivalent(str(cc), concept_canon):
                return True, "canonical_match", 1.0
                
    # Check if any equivalent terms (aliases/canonical forms) are present in the candidate text
    equiv_terms = get_equivalent_terms(concept_lower)
    for term in equiv_terms:
        regex = r'(?<![a-zA-Z0-9_-])' + re.escape(term) + r'(?![a-zA-Z0-9_-])'
        if re.search(regex, cand_lower):
            return True, "canonical_match", 1.0
            
    # 1. Exact Match
    if concept_lower in cand_lower:
        return True, "exact", 1.0
        
    # 2. Abbreviation Expansion
    norm_concept = expand_abbreviations(concept_lower)
    norm_cand = expand_abbreviations(cand_lower)
    if norm_concept in norm_cand:
        return True, "abbreviation", 1.0
        
    # 3. Concept Synonyms
    concept_synonyms = getattr(config, "CONCEPT_SYNONYMS", {})
    synonyms = concept_synonyms.get(concept_lower, [])
    for syn in synonyms:
        if syn in cand_lower or expand_abbreviations(syn) in norm_cand:
            return True, "synonym", 1.0
            
    # Check individual word synonyms for multi-word concepts
    words = concept_lower.split()
    if len(words) > 1:
        word_matches = []
        for w in words:
            w_syns = [w] + concept_synonyms.get(w, [])
            found_w = False
            for ws in w_syns:
                if ws in cand_lower or expand_abbreviations(ws) in norm_cand:
                    found_w = True
                    break
            word_matches.append(found_w)
        if all(word_matches):
            return True, "word_synonym", 1.0

    # 4. Phrase Similarity (SentenceTransformer comparison of multi-word concepts)
    # Moved BEFORE Lemma Match (Issue 3) — embeddings capture compound concepts better.
    if len(concept_lower.split()) > 1 and st_model is not None and get_cached_embedding_fn is not None:
        # Reuse pre-extracted candidate concepts (Issue 4) or extract lazily
        if cand_concepts_precomputed is not None:
            cand_concepts_for_phrase = cand_concepts_precomputed
        else:
            cand_concepts_for_phrase, _ = extract_concepts_with_compounds(cand_doc)
        cand_multi_words = [c for c in cand_concepts_for_phrase if len(c.split()) > 1]
        if cand_multi_words:
            emb_concept = get_cached_embedding_fn(concept_lower, st_model)
            phrase_threshold = getattr(config, "CONCEPT_PHRASE_SIMILARITY_THRESHOLD", 0.82)
            import torch
            for cm in cand_multi_words:
                emb_cm = get_cached_embedding_fn(cm, st_model)
                with torch.inference_mode():
                    sim = float(torch.nn.functional.cosine_similarity(emb_concept.unsqueeze(0), emb_cm.unsqueeze(0)).item())
                if sim >= phrase_threshold:
                    return True, "phrase_similarity", sim

    # 5. Lemma Match (Issue 3 — moved after Phrase Similarity)
    concept_doc = get_spacy_doc(concept_lower)
    concept_lemmas = [t.lemma_ for t in concept_doc if not t.is_stop and t.pos_ in ("NOUN", "PROPN", "ADJ", "VERB")]
    if concept_lemmas:
        cand_lemmas = [t.lemma_ for t in cand_doc]
        if all(lemma in cand_lemmas for lemma in concept_lemmas):
            return True, "lemma", 1.0
            
    # 6. Semantic Similarity
    if st_model is not None and get_cached_embedding_fn is not None:
        emb_concept = get_cached_embedding_fn(concept_lower, st_model)
        emb_cand = get_cached_embedding_fn(cand_text, st_model)
        import torch
        with torch.inference_mode():
            sim = float(torch.nn.functional.cosine_similarity(emb_concept.unsqueeze(0), emb_cand.unsqueeze(0)).item())
        concept_semantic_threshold = getattr(config, "CONCEPT_SEMANTIC_THRESHOLD", 0.75)
        if sim >= concept_semantic_threshold:
            return True, "semantic", sim
        return False, "no_match", sim
        
    return False, "no_match", 0.0

def validate_concepts(original_q, candidate_q, st_model=None, get_cached_embedding_fn=None) -> tuple:
    """
    Evaluates concept preservation between original and candidate questions.
    Supports passing raw strings or NLPContext objects.
    Issue 4: Candidate concepts are extracted once and passed into check_concept_match
    for every original concept loop iteration, avoiding repeated extraction.
    Returns: (score, details_dict)
    """
    from question_profile import QuestionProfile

    if isinstance(original_q, QuestionProfile):
        orig_concepts = original_q.concepts
        orig_compounds = {c for c in orig_concepts if " " in c}
        original_text = original_q.normalized_question
    elif hasattr(original_q, "text"):  # NLPContext
        orig_ctx = original_q
        original_text = orig_ctx.text
        orig_concepts, orig_compounds = extract_concepts_with_compounds(orig_ctx)
    else:
        original_text = original_q
        orig_concepts, orig_compounds = extract_concepts_with_compounds(original_q)

    if isinstance(candidate_q, QuestionProfile):
        candidate_text = candidate_q.normalized_question
        cand_doc = get_spacy_doc(candidate_text)
        cand_concepts_pre = candidate_q.concepts
        cand_compounds_pre = {c for c in cand_concepts_pre if " " in c}
        cand_ctx = candidate_text
    elif hasattr(candidate_q, "text"):  # NLPContext
        cand_ctx = candidate_q
        candidate_text = cand_ctx.text
        cand_doc = cand_ctx.doc
        cand_concepts_pre, cand_compounds_pre = cand_ctx.concepts_and_compounds
    else:
        cand_ctx = candidate_q
        candidate_text = candidate_q
        cand_doc = get_spacy_doc(candidate_q)
        cand_concepts_pre, cand_compounds_pre = extract_concepts_with_compounds(cand_doc)

    concept_stage_score = getattr(config, "CONCEPT_STAGE_SCORE", 25.0)
    
    if not orig_concepts:
        return concept_stage_score, {
            "preservation_percentage": 1.0, 
            "original_concepts": [], 
            "matched_concepts": [], 
            "missing_concepts": [],
            "match_details": {}
        }
        
    matched = []
    missing = []
    match_details = {}
    
    total_weight = 0.0
    matched_weight = 0.0
    compound_weight_val = getattr(config, "CONCEPT_COMPOUND_WEIGHT", 1.5)
    
    for concept in orig_concepts:
        weight = compound_weight_val if concept in orig_compounds else 1.0
        total_weight += weight
        
        is_matched, method, sim_score = check_concept_match(
            concept,
            cand_ctx,
            cand_doc,
            st_model,
            get_cached_embedding_fn,
            cand_concepts_precomputed=cand_concepts_pre,
            cand_compounds_precomputed=cand_compounds_pre,
        )
        
        match_details[concept] = {
            "method": method,
            "similarity": round(sim_score, 4),
            "weight": weight
        }
        
        if is_matched:
            matched.append(concept)
            matched_weight += weight
        else:
            missing.append(concept)
            
    preservation = matched_weight / total_weight if total_weight > 0 else 0.0
    score = round(concept_stage_score * preservation, 2)
    
    from knowledge.concepts import detect_duplicate_equivalent_terms
    dup_aliases = detect_duplicate_equivalent_terms(cand_concepts_pre)
    
    return score, {
        "preservation_percentage": preservation,
        "original_concepts": list(orig_concepts),
        "matched_concepts": matched,
        "missing_concepts": missing,
        "match_details": match_details,
        "duplicate_aliases": dup_aliases
    }
