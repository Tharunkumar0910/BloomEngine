from typing import Dict, Any
import time
import config
from validation_models import ValidationEngineOutput
from concept_validator import validate_concepts
from entity_validator import validate_entities
from number_validator import validate_numbers
from semantic_validator import validate_semantics
from duplicate_validator import validate_duplicates
from grammar_validator import validate_grammar_and_formatting
from bloom_validator import validate_bloom_verbs
from spacy_utils import NLPContext

def evaluate_candidate(
    original_q: str,
    candidate_q: str,
    target_bloom: str,
    target_difficulty: str,
    seen_questions: set,
    session_seen: list,
    config_mode: dict,
    deberta_classifier_fn,
    st_model,
    get_cached_embedding_fn,
    validate_bloom_verbs_fn=None,
    is_final_round: bool = False
) -> ValidationEngineOutput:
    """
    Orchestrates the modular NLP validation engine using a shared NLPContext.
    Enforces the exact 7-stage sequence:
    1. Bloom Classification
    2. Concept Preservation
    3. Technical Entity Preservation
    4. Number Preservation
    5. Semantic Validation
    6. Duplicate Detection
    7. Grammar & Repetition
    
    Every candidate passes through all stages before ranking.
    """
    detailed_metrics = {}
    
    if validate_bloom_verbs_fn is None:
        validate_bloom_verbs_fn = validate_bloom_verbs
 
    # Initialize shared NLP contexts for original and candidate questions
    # (Text normalization happens at NLPContext creation)
    if isinstance(original_q, NLPContext):
        orig_ctx = original_q
    else:
        orig_ctx = NLPContext(original_q, st_model, get_cached_embedding_fn)

    if isinstance(candidate_q, NLPContext):
        cand_ctx = candidate_q
    else:
        cand_ctx = NLPContext(candidate_q, st_model, get_cached_embedding_fn)
 
    # Load Stage Scores from config.py
    bloom_stage_score = getattr(config, "BLOOM_STAGE_SCORE", 35.0)
    concept_stage_score = getattr(config, "CONCEPT_STAGE_SCORE", 25.0)
    entity_score_max = getattr(config, "ENTITY_SCORE", 15.0)
    semantic_score_max = getattr(config, "SEMANTIC_SCORE", 10.0)
    number_score_max = getattr(config, "NUMBER_SCORE", 5.0)
    duplicate_score_max = getattr(config, "DUPLICATE_SCORE", 5.0)
    grammar_score_max = getattr(config, "GRAMMAR_SCORE", 5.0)
    
    pass_threshold = getattr(config, "PASS_THRESHOLD", 80.0)
 
    t_start = time.time()
 
    # ── STAGE 1: Bloom Classification ──
    t0 = time.time()
    pred_bloom, pred_diff, conf = deberta_classifier_fn(cand_ctx.text)
    t_bloom = time.time() - t0
    detailed_metrics["bloom"] = {
        "predicted_bloom": pred_bloom,
        "predicted_difficulty": pred_diff,
        "confidence": conf
    }
    if pred_bloom != target_bloom:
        bloom_score = 0.0
    else:
        confidence = max(conf, 60.0)
        bloom_score = (
            24.0
            + ((confidence - 60.0) / 40.0) * 11.0
        )
        bloom_score = min(35.0, bloom_score)
        bloom_score = round(bloom_score, 2)
 
    # ── STAGE 2: Concept Preservation ──
    t0 = time.time()
    concept_score, concept_details = validate_concepts(
        original_q=orig_ctx,
        candidate_q=cand_ctx,
        st_model=st_model,
        get_cached_embedding_fn=get_cached_embedding_fn
    )
    t_concept = time.time() - t0
    detailed_metrics["concept"] = concept_details
 
    # ── STAGE 3: Technical Entity Preservation ──
    t0 = time.time()
    entity_score, entity_details = validate_entities(
        original_q=orig_ctx,
        candidate_q=cand_ctx,
        st_model=st_model,
        get_cached_embedding_fn=get_cached_embedding_fn
    )
    t_entity = time.time() - t0
    detailed_metrics["entity"] = entity_details
 
    # ── STAGE 4: Number Preservation ──
    t0 = time.time()
    number_score, number_details = validate_numbers(orig_ctx, cand_ctx)
    t_number = time.time() - t0
    detailed_metrics["number"] = number_details
 
    # ── STAGE 5: Semantic Validation ──
    t0 = time.time()
    semantic_score, semantic_details = validate_semantics(
        original_q=orig_ctx,
        candidate_q=cand_ctx,
        st_model=st_model,
        get_cached_embedding_fn=get_cached_embedding_fn
    )
    t_semantic = time.time() - t0
    detailed_metrics["semantic"] = semantic_details
 
    # ── STAGE 6: Duplicate Detection ──
    t0 = time.time()
    duplicate_score, duplicate_details = validate_duplicates(
        candidate_q=cand_ctx,
        seen_questions=seen_questions,
        session_seen=session_seen,
        config_mode=config_mode,
        st_model=st_model,
        get_cached_embedding_fn=get_cached_embedding_fn,
        is_final_round=is_final_round
    )
    t_duplicate = time.time() - t0
    detailed_metrics["duplicate"] = duplicate_details
 
    # ── STAGE 7: Grammar & Repetition ──
    t0 = time.time()
    grammar_score, grammar_details = validate_grammar_and_formatting(cand_ctx.text)
    t_grammar = time.time() - t0
    detailed_metrics["grammar"] = grammar_details
 
    # ── Non-fatal Verb Warning Penalty (Subtracted from Total Score) ──
    is_valid_verb, verb_fail_reason = validate_bloom_verbs_fn(cand_ctx.text, target_bloom)
    verb_penalty = 0.0
    detailed_metrics["bloom_verb"] = {
        "is_valid": is_valid_verb,
        "warning": verb_fail_reason if not is_valid_verb else "None"
    }
    if not is_valid_verb:
        verb_penalty = getattr(config, "BLOOM_VERB_PENALTY", 2.0)
 
    # ── CALCULATE TOTAL SCORE ──
    total_score = (
        bloom_score +
        concept_score +
        entity_score +
        number_score +
        semantic_score +
        duplicate_score +
        grammar_score -
        verb_penalty
    )
    total_score = round(max(0.0, total_score), 2)
    
    # ── DETERMINING PASS STATUS & REJECTION REASON ──
    # Check hard validation failure conditions
    is_mismatch = pred_bloom != target_bloom
    is_duplicate = duplicate_details.get("is_duplicate", False)
    is_too_short = grammar_details.get("is_too_short", False) or not cand_ctx.text
    is_below_threshold = total_score < pass_threshold
    
    if is_mismatch or is_duplicate or is_too_short or is_below_threshold:
        passed = False
    else:
        passed = True
        
    rejection_reason = "None"
    if not passed:
        if is_mismatch:
            rejection_reason = "Classification Mismatch"
        elif is_duplicate:
            rejection_reason = "Duplicate"
        elif is_too_short:
            rejection_reason = "Too Short"
        else:
            # Attribute rejection to the stage that lost the most relative points
            losses = {
                "Classification Mismatch": bloom_stage_score - bloom_score,
                "Concept Drift": concept_stage_score - concept_score,
                "Entity Mismatch": entity_score_max - entity_score,
                "Semantic Drift": semantic_score_max - semantic_score,
                "Numbers Mismatch": number_score_max - number_score,
                "Duplicate": duplicate_score_max - duplicate_score,
                "Repetition": grammar_score_max - grammar_score
            }
            if not is_valid_verb:
                losses["Verb Penalty"] = verb_penalty
                
            rejection_reason = max(losses, key=losses.get)
            
    if getattr(config, "DEBUG", False):
        print(f"[DEBUG] Validation Engine Profile for candidate: {cand_ctx.text[:40]}...")
        print(f"  Stage 1 (Bloom):     {t_bloom*1000:.2f} ms")
        print(f"  Stage 2 (Concept):   {t_concept*1000:.2f} ms")
        print(f"  Stage 3 (Entity):    {t_entity*1000:.2f} ms")
        print(f"  Stage 4 (Number):    {t_number*1000:.2f} ms")
        print(f"  Stage 5 (Semantic):  {t_semantic*1000:.2f} ms")
        print(f"  Stage 6 (Duplicate): {t_duplicate*1000:.2f} ms")
        print(f"  Stage 7 (Grammar):   {t_grammar*1000:.2f} ms")
        print(f"  Total Time:          {(time.time() - t_start)*1000:.2f} ms")

    return ValidationEngineOutput(
        bloom_score=bloom_score,
        concept_score=concept_score,
        entity_score=entity_score,
        number_score=number_score,
        semantic_score=semantic_score,
        duplicate_score=duplicate_score,
        grammar_score=grammar_score,
        total_score=total_score,
        passed=passed,
        rejection_reason=rejection_reason,
        detailed_metrics=detailed_metrics
    )

