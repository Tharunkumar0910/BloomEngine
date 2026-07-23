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
from question_profile import QuestionProfile
from question_understanding import QuestionUnderstandingEngine
from knowledge_consistency_validator import validate_knowledge_consistency
from topic_validator import validate_topic

def evaluate_candidate(
    original_q,
    candidate_q,
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
    Orchestrates the modular NLP validation engine using QuestionProfile.
    Enforces the exact 7-stage sequence with new domain/topic checks and weighted ranking.
    """
    detailed_metrics = {}
    
    if validate_bloom_verbs_fn is None:
        validate_bloom_verbs_fn = validate_bloom_verbs
 
    # Build QuestionProfiles
    if isinstance(original_q, QuestionProfile):
        orig_prof = original_q
    else:
        orig_prof = QuestionUnderstandingEngine.build_profile(original_q)

    if isinstance(candidate_q, QuestionProfile):
        cand_prof = candidate_q
    else:
        cand_prof = QuestionUnderstandingEngine.build_profile(candidate_q, target_bloom)

    # Load Stage Scores and Weights from config.py
    w_bloom = config.VALIDATION_WEIGHTS.get("bloom", 35.0)
    w_domain = config.VALIDATION_WEIGHTS.get("domain", 20.0)
    w_topic = config.VALIDATION_WEIGHTS.get("topic", 15.0)
    w_concept = config.VALIDATION_WEIGHTS.get("concept", 10.0)
    w_entity = config.VALIDATION_WEIGHTS.get("entity", 10.0)
    w_number = config.VALIDATION_WEIGHTS.get("number", 5.0)
    w_grammar = config.VALIDATION_WEIGHTS.get("grammar", 3.0)
    w_duplicate = config.VALIDATION_WEIGHTS.get("duplicate", 2.0)
    
    pass_threshold = getattr(config, "PASS_THRESHOLD", 80.0)

    # Load active validation profile thresholds
    _profiles = getattr(config, "VALIDATION_PROFILES", {})
    _active   = getattr(config, "ACTIVE_VALIDATION_PROFILE", "balanced")
    _profile  = _profiles.get(_active, {})
    semantic_threshold = _profile.get("semantic_drift_threshold", 0.70)

    t_start = time.time()
 
    # ── STAGE 1: Bloom Classification ──
    t0 = time.time()
    pred_bloom, pred_diff, conf = deberta_classifier_fn(cand_prof.normalized_question)
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
    
    scaled_bloom_score = round((bloom_score / 35.0) * w_bloom, 2) if bloom_score > 0 else 0.0

    # ── STAGE 2: Concept Preservation ──
    t0 = time.time()
    concept_score, concept_details = validate_concepts(
        original_q=orig_prof,
        candidate_q=cand_prof,
        st_model=st_model,
        get_cached_embedding_fn=get_cached_embedding_fn
    )
    t_concept = time.time() - t0
    detailed_metrics["concept"] = concept_details
    concept_ratio = concept_details.get("preservation_percentage", 0.0)
    scaled_concept_score = round(concept_ratio * w_concept, 2)

    # ── STAGE 3: Technical Entity Preservation ──
    t0 = time.time()
    entity_score, entity_details = validate_entities(
        original_q=orig_prof,
        candidate_q=cand_prof,
        st_model=st_model,
        get_cached_embedding_fn=get_cached_embedding_fn
    )
    t_entity = time.time() - t0
    detailed_metrics["entity"] = entity_details
    entity_score_max = getattr(config, "ENTITY_SCORE", 15.0)
    entity_ratio = (entity_score / entity_score_max) if entity_score_max > 0 else 0.0
    scaled_entity_score = round(entity_ratio * w_entity, 2)

    # ── STAGE 4: Number Preservation ──
    t0 = time.time()
    number_score, number_details = validate_numbers(orig_prof, cand_prof)
    t_number = time.time() - t0
    detailed_metrics["number"] = number_details
    number_ratio = number_details.get("preservation_ratio", 0.0)
    scaled_number_score = round(number_ratio * w_number, 2)

    # ── STAGE 5: Knowledge Consistency ──
    t0 = time.time()
    knowledge_score, knowledge_details = validate_knowledge_consistency(
        orig_prof, cand_prof, st_model, get_cached_embedding_fn
    )
    t_knowledge = time.time() - t0
    is_domain_drift = knowledge_details.get("domain_drift", False)
    detailed_metrics["knowledge"] = knowledge_details

    # ── STAGE 6: Semantic Validation ──
    t0 = time.time()
    semantic_score, semantic_details = validate_semantics(
        original_q=orig_prof,
        candidate_q=cand_prof,
        st_model=st_model,
        get_cached_embedding_fn=get_cached_embedding_fn
    )
    t_semantic = time.time() - t0
    detailed_metrics["semantic"] = semantic_details


    # ── STAGE 6: Duplicate Detection ──
    t0 = time.time()
    duplicate_score, duplicate_details = validate_duplicates(
        candidate_q=cand_prof,
        seen_questions=seen_questions,
        session_seen=session_seen,
        config_mode=config_mode,
        st_model=st_model,
        get_cached_embedding_fn=get_cached_embedding_fn,
        is_final_round=is_final_round
    )
    t_duplicate = time.time() - t0
    detailed_metrics["duplicate"] = duplicate_details
    duplicate_score_max = getattr(config, "DUPLICATE_SCORE", 5.0)
    duplicate_ratio = (duplicate_score / duplicate_score_max) if duplicate_score_max > 0 else 0.0
    scaled_duplicate_score = round(duplicate_ratio * w_duplicate, 2)

    # ── STAGE 7: Grammar & Repetition ──
    t0 = time.time()
    grammar_score, grammar_details = validate_grammar_and_formatting(cand_prof.normalized_question)
    t_grammar = time.time() - t0
    detailed_metrics["grammar"] = grammar_details
    grammar_score_max = getattr(config, "GRAMMAR_SCORE", 5.0)
    grammar_ratio = (grammar_score / grammar_score_max) if grammar_score_max > 0 else 0.0
    scaled_grammar_score = round(grammar_ratio * w_grammar, 2)

    # ── Domain Validation ──
    t0 = time.time()
    if cand_prof.domain.lower() == orig_prof.domain.lower():
        domain_score_ratio = 1.0
    else:
        orig_kws = set(orig_prof.matched_domain_keywords)
        cand_kws = set(cand_prof.matched_domain_keywords)
        if orig_kws:
            domain_score_ratio = 0.5 * (len(orig_kws & cand_kws) / len(orig_kws))
        else:
            domain_score_ratio = 0.0
            
    domain_score = round(domain_score_ratio * w_domain, 2)
    t_domain = time.time() - t0
    
    detailed_metrics["domain"] = {
        "original_domain": orig_prof.domain,
        "candidate_domain": cand_prof.domain,
        "original_domain_keywords": list(orig_prof.matched_domain_keywords),
        "candidate_domain_keywords": list(cand_prof.matched_domain_keywords),
        "preservation_ratio": domain_score_ratio
    }

    # ── Topic Validation ──
    t0 = time.time()
    topic_score_ratio = validate_topic(orig_prof, cand_prof)
    topic_score = round(topic_score_ratio * w_topic, 2)
    t_topic = time.time() - t0
    
    detailed_metrics["topic"] = {
        "original_topic": orig_prof.topic,
        "candidate_topic": cand_prof.topic,
        "original_topic_keywords": list(orig_prof.matched_topic_keywords),
        "candidate_topic_keywords": list(cand_prof.matched_topic_keywords),
        "preservation_ratio": topic_score_ratio
    }

    # ── Non-fatal Verb Warning Penalty (Subtracted from Total Score) ──
    is_valid_verb, verb_fail_reason = validate_bloom_verbs_fn(cand_prof.normalized_question, target_bloom)
    verb_penalty = 0.0
    detailed_metrics["bloom_verb"] = {
        "is_valid": is_valid_verb,
        "warning": verb_fail_reason if not is_valid_verb else "None"
    }
    if not is_valid_verb:
        verb_penalty = getattr(config, "BLOOM_VERB_PENALTY", 2.0)
 
    # ── CALCULATE TOTAL SCORE ──
    total_score = (
        scaled_bloom_score +
        domain_score +
        topic_score +
        scaled_concept_score +
        scaled_entity_score +
        scaled_number_score +
        scaled_grammar_score +
        scaled_duplicate_score -
        verb_penalty -
        (8.0 if is_domain_drift else 0.0)   # domain drift soft penalty
    )
    total_score = round(max(0.0, total_score), 2)
    
    # ── DETERMINING PASS STATUS & REJECTION REASON ──
    is_mismatch      = pred_bloom != target_bloom
    is_duplicate     = duplicate_details.get("is_duplicate", False)
    is_too_short     = grammar_details.get("is_too_short", False) or not cand_prof.normalized_question
    is_semantic_drift = semantic_details.get("similarity", 1.0) < semantic_threshold
    is_below_threshold = total_score < pass_threshold
    has_duplicate_aliases = len(concept_details.get("duplicate_aliases", [])) > 0

    if is_mismatch or is_duplicate or is_too_short or is_semantic_drift or is_below_threshold or has_duplicate_aliases:
        passed = False
    else:
        passed = True

    rejection_reason = "None"
    if not passed:
        if is_mismatch:
            rejection_reason = "Classification Mismatch"
        elif has_duplicate_aliases:
            rejection_reason = "Duplicate Technical Concept"
        elif is_duplicate:
            rejection_reason = "Duplicate"
        elif is_too_short:
            rejection_reason = "Too Short"
        elif is_semantic_drift:
            rejection_reason = "Semantic Drift"
        elif is_domain_drift:
            rejection_reason = "Domain Drift"
        else:
            # Attribute rejection to the stage that lost the most relative points
            losses = {
                "Classification Mismatch": w_bloom - scaled_bloom_score,
                "Domain Mismatch": w_domain - domain_score,
                "Topic Mismatch": w_topic - topic_score,
                "Concept Drift": w_concept - scaled_concept_score,
                "Entity Mismatch": w_entity - scaled_entity_score,
                "Numbers Mismatch": w_number - scaled_number_score,
                "Duplicate": w_duplicate - scaled_duplicate_score,
                "Repetition": w_grammar - scaled_grammar_score
            }
            if not is_valid_verb:
                losses["Verb Penalty"] = verb_penalty
                
            rejection_reason = max(losses, key=losses.get)
            
    if getattr(config, "DEBUG", False):
        print(f"[DEBUG] Stage 1 (Bloom):       {t_bloom*1000:.2f} ms")
        print(f"  Stage 5 (Knowledge):      {t_knowledge*1000:.2f} ms")
        print(f"  Total:                    {(time.time() - t_start)*1000:.2f} ms")

    return ValidationEngineOutput(
        bloom_score=scaled_bloom_score,
        concept_score=scaled_concept_score,
        entity_score=scaled_entity_score,
        number_score=scaled_number_score,
        semantic_score=semantic_score,
        duplicate_score=scaled_duplicate_score,
        grammar_score=scaled_grammar_score,
        domain_score=domain_score,
        topic_score=topic_score,
        total_score=total_score,
        passed=passed,
        rejection_reason=rejection_reason,
        detailed_metrics=detailed_metrics,
        knowledge_score=knowledge_score,
        knowledge_details=knowledge_details,
        validation_explanation=knowledge_details.get("validation_explanation", {}),
        domain_drift=is_domain_drift,
    )
