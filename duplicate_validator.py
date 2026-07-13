from functools import lru_cache
import string
import config
from rapidfuzz import fuzz

@lru_cache(maxsize=1024)
def get_fingerprint(text: str) -> str:
    """Helper to remove punctuation and generic Bloom verbs to create a question fingerprint."""
    text = text.lower()
    for p in string.punctuation:
        text = text.replace(p, "")
    words = text.split()
    bloom_verbs = getattr(config, "DUPLICATE_IGNORE_BLOOM_VERBS", set())
    filtered = [w for w in words if w not in bloom_verbs]
    return " ".join(filtered)

def validate_duplicates(
    candidate_q, 
    seen_questions: set, 
    session_seen: list, 
    config_mode: dict, 
    st_model, 
    get_cached_embedding_fn,
    is_final_round: bool = False
) -> tuple:
    """
    Validates that a candidate is not a duplicate.
    Returns: (score, details_dict)
    """
    if hasattr(candidate_q, "text"):  # NLPContext
        candidate_text = candidate_q.text
    else:
        candidate_text = candidate_q
        
    gen_fingerprint = get_fingerprint(candidate_text)
    is_duplicate = False
    max_duplicate_ratio = 0.0
    
    # Read thresholds from config/mode
    _final_thr = getattr(config, "DUPLICATE_FINAL_ROUND_THRESHOLD", 0.97)
    recent_threshold = _final_thr if is_final_round else config_mode.get("duplicate_threshold_recent", 0.85)
    session_threshold = _final_thr if is_final_round else config_mode.get("duplicate_threshold_session", 0.85)
    
    config_semantic_threshold = getattr(config, "DUPLICATE_SEMANTIC_THRESHOLD", 0.93)
    semantic_threshold = _final_thr if is_final_round else config_semantic_threshold
    
    # 1. RapidFuzz checks
    for seen_q in seen_questions:
        ratio = fuzz.ratio(gen_fingerprint, get_fingerprint(seen_q)) / 100.0
        if ratio > max_duplicate_ratio:
            max_duplicate_ratio = ratio
        if ratio > recent_threshold:
            is_duplicate = True
            
    for seen_q in session_seen:
        ratio = fuzz.ratio(gen_fingerprint, get_fingerprint(seen_q)) / 100.0
        if ratio > max_duplicate_ratio:
            max_duplicate_ratio = ratio
        if ratio > session_threshold:
            is_duplicate = True
            
    # 2. Semantic duplicate check
    if not is_duplicate and st_model is not None and get_cached_embedding_fn is not None:
        all_seen = list(seen_questions) + list(session_seen)
        if all_seen:
            try:
                import torch as _torch
                if hasattr(candidate_q, "get_embedding"):
                    gen_emb = candidate_q.get_embedding()
                else:
                    gen_emb = get_cached_embedding_fn(candidate_text, st_model)
                for seen in all_seen:
                    seen_emb = get_cached_embedding_fn(seen, st_model)
                    with _torch.inference_mode():
                        sim = float(_torch.nn.functional.cosine_similarity(
                            gen_emb.unsqueeze(0), seen_emb.unsqueeze(0)
                        ).item())
                    if sim > max_duplicate_ratio:
                        max_duplicate_ratio = sim
                    if sim >= semantic_threshold:
                        is_duplicate = True
                        break
            except Exception as exc:
                print(f"[WARNING] Semantic duplicate check error in validator: {exc}")
                
    duplicate_score_max = getattr(config, "DUPLICATE_SCORE", 5.0)
    score = 0.0 if is_duplicate else duplicate_score_max
    
    return score, {
        "is_duplicate": is_duplicate,
        "max_duplicate_ratio": max_duplicate_ratio,
        "recent_threshold": recent_threshold,
        "session_threshold": session_threshold,
        "semantic_threshold": semantic_threshold
    }

