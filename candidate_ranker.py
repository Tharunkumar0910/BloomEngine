from validation_models import ValidationEngineOutput

def calculate_nlp_rank_score(validation_output: ValidationEngineOutput) -> float:
    """
    Computes a single float Rank Score for UI/log compatibility.
    Passed candidates get a huge boost to ensure they rank above failed ones.
    Within passed/failed groups, sorting is determined by the total NLP validation score.
    """
    is_passed_val = 1.0 if validation_output.passed else 0.0
    return (1000000.0 * is_passed_val) + validation_output.total_score

def rank_candidates(candidates_with_outputs: list) -> list:
    """
    Sorts a list of (candidate_dict, ValidationEngineOutput) pairs.
    Priority: passed → bloom_confidence → concept_preservation → semantic_similarity →
              knowledge_score → concept_score → entity_score → grammar_score → total_score →
              -latency_ms → -attempt_number
    """
    def sort_key(item):
        c_dict, val_out = item
        passed          = 1 if val_out.passed else 0
        bloom_metrics   = val_out.detailed_metrics.get("bloom", {})
        bloom_confidence= bloom_metrics.get("confidence", 0.0)
        
        concept_data = val_out.detailed_metrics.get("concept", {}) or {}
        concept_pres = concept_data.get("preservation_percentage", 0.0)
        
        semantic_data = val_out.detailed_metrics.get("semantic", {}) or {}
        semantic_sim = semantic_data.get("similarity", 0.0)
        
        knowledge_score = getattr(val_out, "knowledge_score", 0.0)
        concept_score   = val_out.concept_score
        entity_score    = val_out.entity_score
        grammar_score   = val_out.grammar_score
        total_score     = val_out.total_score
        latency_ms      = getattr(val_out, "generation_time_ms", 0.0)
        attempt_number  = c_dict.get("attempt_number", c_dict.get("Generation Round", 1))
        return (
            passed,
            bloom_confidence,
            concept_pres,
            semantic_sim,
            knowledge_score,
            concept_score,
            entity_score,
            grammar_score,
            total_score,
            -latency_ms,
            -attempt_number,
        )
    return sorted(candidates_with_outputs, key=sort_key, reverse=True)


def rank_candidates_dicts(candidates: list) -> list:
    """
    Sorts a list of candidate dictionaries using the exact same logic.
    """
    def sort_key(c):
        passed = 1 if c.get("validation_status") == "Pass" or c.get("Validation Status") == "Pass" else 0
        total_score = c.get("Total Score", c.get("total_score", 0.0))
        bloom_score = c.get("Bloom Score", c.get("bloom_score", 0.0))
        domain_score = c.get("Domain Score", c.get("domain_score", 0.0))
        topic_score = c.get("Topic Score", c.get("topic_score", 0.0))
        
        def safe_float(v):
            if v is None:
                return 0.0
            if isinstance(v, (int, float)):
                return float(v)
            try:
                if "/" in str(v):
                    parts = str(v).split("/")
                    return float(parts[0]) / float(parts[1])
                return float(v)
            except Exception:
                return 0.0
                
        concept_pres = safe_float(c.get("concept_similarity_score", 0.0))
        semantic_sim = safe_float(c.get("concept_similarity_score_raw", c.get("semantic_score", 0.0)))
        
        concept_score = safe_float(c.get("concept_score", 0.0))
        entity_score = safe_float(c.get("Entity Score", c.get("entity_score", 0.0)))
        semantic_score = safe_float(c.get("Semantic Score", c.get("semantic_score", 0.0)))
        number_score = safe_float(c.get("Number Score", c.get("number_score", 0.0)))
        grammar_score = safe_float(c.get("Grammar Score", c.get("grammar_score", 0.0)))
        
        bloom_confidence = safe_float(c.get("Confidence", c.get("confidence", 0.0)))
        attempt_number = c.get("attempt_number", c.get("Generation Round", 1))
        
        return (
            passed,
            total_score,
            bloom_score,
            concept_pres,
            semantic_sim,
            domain_score,
            topic_score,
            concept_score,
            entity_score,
            semantic_score,
            number_score,
            grammar_score,
            bloom_confidence,
            -attempt_number
        )

    return sorted(candidates, key=sort_key, reverse=True)
