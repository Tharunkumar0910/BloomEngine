import torch
import config
from concept_validator import extract_concepts_with_compounds

def validate_semantics(original_q, candidate_q, st_model, get_cached_embedding_fn) -> tuple:
    """
    Validates semantic similarity between original and candidate questions.
    Compares each original concept/entity to its closest candidate counterpart and averages similarities.
    Returns: (score, details_dict)
    """
    if st_model is None or get_cached_embedding_fn is None:
        # Fallback if model is not ready
        return 10.0, {"similarity": 1.0, "method": "fallback"}
        
    if hasattr(original_q, "concepts"):  # NLPContext
        orig_concepts = original_q.concepts
    else:
        from concept_validator import extract_concepts_with_compounds
        orig_concepts, _ = extract_concepts_with_compounds(original_q)
        
    if hasattr(candidate_q, "concepts"):  # NLPContext
        cand_concepts = candidate_q.concepts
    else:
        from concept_validator import extract_concepts_with_compounds
        cand_concepts, _ = extract_concepts_with_compounds(candidate_q)
        
    if orig_concepts and cand_concepts:
        # Pre-retrieve embeddings for all candidate concepts
        cand_embs = {c: get_cached_embedding_fn(c, st_model) for c in cand_concepts}
        
        similarities = []
        for o_c in orig_concepts:
            emb_o = get_cached_embedding_fn(o_c, st_model)
            best_sim = 0.0
            for c_c, emb_c in cand_embs.items():
                with torch.inference_mode():
                    sim = float(torch.nn.functional.cosine_similarity(emb_o.unsqueeze(0), emb_c.unsqueeze(0)).item())
                if sim > best_sim:
                    best_sim = sim
            similarities.append(best_sim)
            
        similarity = sum(similarities) / len(similarities) if similarities else 0.0
        orig_semantic_str = ", ".join(sorted(list(orig_concepts)))
        cand_semantic_str = ", ".join(sorted(list(cand_concepts)))
    else:
        # Fallback: whole-sentence similarity
        if hasattr(original_q, "get_embedding"):
            emb_orig = original_q.get_embedding()
            orig_text = original_q.text
        else:
            emb_orig = get_cached_embedding_fn(original_q, st_model)
            orig_text = original_q
            
        if hasattr(candidate_q, "get_embedding"):
            emb_cand = candidate_q.get_embedding()
            cand_text = candidate_q.text
        else:
            emb_cand = get_cached_embedding_fn(candidate_q, st_model)
            cand_text = candidate_q
            
        with torch.inference_mode():
            similarity = float(torch.nn.functional.cosine_similarity(emb_orig.unsqueeze(0), emb_cand.unsqueeze(0)).item())
        orig_semantic_str = orig_text
        cand_semantic_str = cand_text
        
    semantic_score_max = getattr(config, "SEMANTIC_SCORE", 10.0)
    score = round(semantic_score_max * max(0.0, similarity), 2)
    
    return score, {
        "similarity": similarity,
        "original_semantic_text": orig_semantic_str,
        "candidate_semantic_text": cand_semantic_str
    }

