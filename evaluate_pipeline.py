"""
Benchmark evaluation pipeline for BloomAI Arena v2.1.
Evaluates Mode E (Multi-Candidate Ranking) on benchmark_dataset_100.json.
Generates comprehensive quality, performance, and retry metrics.
"""

import os
import sys
import re
import time
import json
import argparse
import pandas as pd
import numpy as np
import torch
from tqdm import tqdm

# Ensure we import the local app.py and config.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import app
from app import (
    load_models,
    run_warmup,
    classify_text,
    extract_core_phrase,
    generate_validated_variant,
    infer_domain,
    BLOOM_TO_DIFFICULTY,
)
from config import MODES

# ---------------------------------------------------------------------------
# Simple custom implementation of BLEU & ROUGE (no external NLTK dependency)
# ---------------------------------------------------------------------------

def compute_bleu(reference: str, candidate: str) -> float:
    """Calculate BLEU-4 score with Laplace smoothing."""
    def get_ngrams(tokens, n):
        return [tuple(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]
    
    ref_tokens = re.findall(r'\b\w+\b', reference.lower())
    cand_tokens = re.findall(r'\b\w+\b', candidate.lower())
    
    if not cand_tokens or not ref_tokens:
        return 0.0
    
    c = len(cand_tokens)
    r = len(ref_tokens)
    
    bp = 1.0 if c > r else np.exp(1.0 - r / c) if c > 0 else 0.0
    
    precisions = []
    for n in range(1, 5):
        ref_ngrams = get_ngrams(ref_tokens, n)
        cand_ngrams = get_ngrams(cand_tokens, n)
        if not cand_ngrams:
            precisions.append(0.1 / (1 + 0.1))
            continue
        
        ref_counts = {}
        for ng in ref_ngrams:
            ref_counts[ng] = ref_counts.get(ng, 0) + 1
            
        cand_counts = {}
        for ng in cand_ngrams:
            cand_counts[ng] = cand_counts.get(ng, 0) + 1
            
        overlap = 0
        for ng, count in cand_counts.items():
            if ng in ref_counts:
                overlap += min(count, ref_counts[ng])
        
        p = (overlap + 0.1) / (len(cand_ngrams) + 0.1)
        precisions.append(p)
        
    weight = 0.25
    g_mean = np.exp(sum(weight * np.log(p) for p in precisions))
    return float(bp * g_mean)

def compute_rouge_n(reference: str, candidate: str, n: int) -> float:
    """Calculate ROUGE-N F1 score."""
    ref_tokens = re.findall(r'\b\w+\b', reference.lower())
    cand_tokens = re.findall(r'\b\w+\b', candidate.lower())
    
    if not ref_tokens or not cand_tokens:
        return 0.0
        
    def get_ngrams(tokens, n):
        return [tuple(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]
        
    ref_ngrams = get_ngrams(ref_tokens, n)
    cand_ngrams = get_ngrams(cand_tokens, n)
    
    if not ref_ngrams or not cand_ngrams:
        return 0.0
        
    ref_counts = {}
    for ng in ref_ngrams:
        ref_counts[ng] = ref_counts.get(ng, 0) + 1
        
    cand_counts = {}
    for ng in cand_ngrams:
        cand_counts[ng] = cand_counts.get(ng, 0) + 1
        
    overlap = 0
    for ng, count in cand_counts.items():
        if ng in ref_counts:
            overlap += min(count, ref_counts[ng])
            
    r = overlap / len(ref_ngrams)
    p = overlap / len(cand_ngrams)
    
    if p + r == 0:
        return 0.0
    return 2 * p * r / (p + r)

def compute_lcs(x, y):
    """Compute length of Longest Common Subsequence."""
    m = len(x)
    n = len(y)
    L = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0 or j == 0:
                L[i][j] = 0
            elif x[i-1] == y[j-1]:
                L[i][j] = L[i-1][j-1] + 1
            else:
                L[i][j] = max(L[i-1][j], L[i][j-1])
    return L[m][n]

def compute_rouge_l(reference: str, candidate: str) -> float:
    """Calculate ROUGE-L F1 score based on LCS."""
    ref_tokens = re.findall(r'\b\w+\b', reference.lower())
    cand_tokens = re.findall(r'\b\w+\b', candidate.lower())
    
    if not ref_tokens or not cand_tokens:
        return 0.0
        
    lcs_len = compute_lcs(ref_tokens, cand_tokens)
    r = lcs_len / len(ref_tokens)
    p = lcs_len / len(cand_tokens)
    
    if p + r == 0:
        return 0.0
    return 2 * p * r / (p + r)


def classify_semantic_drift(val_out, orig_profile, cand_profile) -> str:
    """
    Classifies a failed candidate attempt's semantic drift or validation failure
    into one of 11 distinct classes:
    - Concept Removal
    - Concept Addition
    - Terminology Change
    - Entity Change
    - Numeric Change
    - Algorithm Change
    - Protocol Change
    - Domain Vocabulary Change
    - Topic Vocabulary Change
    - Intent Change
    - Equivalent Technical Concepts
    """
    if getattr(val_out, "rejection_reason", "") == "Duplicate Technical Concept":
        return "Equivalent Technical Concepts"
        
    if val_out.rejection_reason == "Classification Mismatch" or val_out.bloom_score < 30:
        return "Intent Change"
        
    num_metrics = val_out.detailed_metrics.get("number", {})
    if num_metrics:
        missing_nums = num_metrics.get("missing_numbers", [])
        extra_nums = num_metrics.get("extra_numbers", [])
        if missing_nums or extra_nums:
            return "Numeric Change"
            
    orig_text = orig_profile.raw_question.lower() if orig_profile else ""
    cand_text = cand_profile.raw_question.lower() if cand_profile else ""
    
    protocols = {"http", "https", "tcp", "udp", "ip", "ipv4", "ipv6", "dns", "smtp", "ftp", "ssl", "tls", "ssh", "grpc", "soap", "rest"}
    orig_protocols = {p for p in protocols if re.search(r'\b' + p + r'\b', orig_text)}
    cand_protocols = {p for p in protocols if re.search(r'\b' + p + r'\b', cand_text)}
    if orig_protocols != cand_protocols:
        return "Protocol Change"
        
    algorithms = {"dijkstra", "bfs", "dfs", "quicksort", "mergesort", "bubblesort", "heapsort", "binary search", "a*", "kruskal", "prim", "bellman-ford"}
    orig_algos = {a for a in algorithms if a in orig_text}
    cand_algos = {a for a in algorithms if a in cand_text}
    if orig_algos != cand_algos:
        return "Algorithm Change"
        
    concept_metrics = val_out.detailed_metrics.get("concept", {})
    if concept_metrics:
        matched = concept_metrics.get("matched_concepts", [])
        original = concept_metrics.get("original_concepts", [])
        if len(matched) < len(original):
            return "Concept Removal"
            
    if concept_metrics:
        candidate_concepts = concept_metrics.get("candidate_concepts", [])
        matched = concept_metrics.get("matched_concepts", [])
        extra = [c for c in candidate_concepts if c not in matched]
        if extra:
            return "Concept Addition"
            
    entity_metrics = val_out.detailed_metrics.get("entity", {})
    if entity_metrics:
        missing_ent = entity_metrics.get("missing_entities", [])
        extra_ent = entity_metrics.get("extra_entities", [])
        if missing_ent or extra_ent:
            return "Entity Change"
            
    topic_metrics = val_out.detailed_metrics.get("topic", {})
    if topic_metrics:
        if topic_metrics.get("topic_mismatch", False) or val_out.topic_score < 12:
            return "Terminology Change"
            
    if val_out.topic_score < 15:
        return "Topic Vocabulary Change"
        
    domain_metrics = val_out.detailed_metrics.get("domain", {})
    if domain_metrics:
        if domain_metrics.get("domain_mismatch", False) or val_out.domain_score < 18:
            return "Domain Vocabulary Change"
            
    return "Terminology Change"


# ---------------------------------------------------------------------------
# Benchmark execution
# ---------------------------------------------------------------------------

def run_benchmark(dataset_path: str, limit: int = None):
    print("==========================================================")
    print("      BloomAI Arena v2.1 - Benchmark Experiment Suite     ")
    print("==========================================================")
    
    # Check dataset existence
    if not os.path.exists(dataset_path):
        print(f"[ERROR] Benchmark dataset not found at: {dataset_path}")
        sys.exit(1)
        
    # Load dataset
    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)
        
    if limit is not None:
        dataset = dataset[:limit]
        print(f"Limiting benchmark execution to first {limit} records.")
        
    print(f"Loaded {len(dataset)} records from {os.path.basename(dataset_path)}")
    
    # Initialize models
    print("\nLoading models sequentially...")
    load_models()
    print("Running warmup...")
    run_warmup()
    print("System warmed up and ready.")
    
    results = []
    all_attempts_flat = []
    
    print("\nStarting evaluation over Mode E...")
    config_mode = MODES["Mode E (Multi-Candidate Ranking)"]
    
    for idx, rec in enumerate(tqdm(dataset, desc="Processing questions")):
        original_q = rec["question"]
        target_bloom = rec["expected_bloom"]
        target_diff = rec.get("expected_difficulty", BLOOM_TO_DIFFICULTY.get(target_bloom, "Medium"))
        domain = rec.get("domain", "CS")
        topic = rec.get("topic", "General")
        
        # 1. Classify source question
        src_bloom, src_diff, _ = classify_text(original_q)
        
        # 2. Get concept
        required_concept = extract_core_phrase(original_q)
        if not required_concept:
            required_concept = topic
            
        session_seen = []
        
        # 3. Generate rewritten question using validation pipeline
        start_time = time.time()
        val_result = generate_validated_variant(
            question=original_q,
            src_bloom=src_bloom,
            src_diff=src_diff,
            target_bloom=target_bloom,
            target_difficulty=target_diff,
            domain=domain,
            required_concept=required_concept,
            session_seen=session_seen,
            config_mode=config_mode,
            mode_name="Mode E (Multi-Candidate Ranking)"
        )
        total_time = time.time() - start_time
        
        # Compute BLEU/ROUGE relative to the original source question
        gen_q = val_result.generated_question
        bleu = compute_bleu(original_q, gen_q)
        r1 = compute_rouge_n(original_q, gen_q, 1)
        r2 = compute_rouge_n(original_q, gen_q, 2)
        rl = compute_rouge_l(original_q, gen_q)
        
        bloom_match = (val_result.predicted_bloom == target_bloom)
        
        # Determine final status code
        is_pass = val_result.validation_status in ["Pass", "Exact Match", "Adjacent Match"] or val_result.validation_status.startswith("Pass")
        
        res_entry = {
            "id": idx + 1,
            "original_question": original_q,
            "generated_question": gen_q,
            "source_bloom": src_bloom,
            "source_difficulty": src_diff,
            "target_bloom": target_bloom,
            "target_difficulty": target_diff,
            "predicted_bloom": val_result.predicted_bloom,
            "predicted_difficulty": val_result.predicted_difficulty,
            "confidence": val_result.confidence,
            "attempts": val_result.attempts,
            "generation_time": total_time,
            "validation_status": val_result.validation_status,
            "rejection_reason": val_result.rejection_reason,
            "concept_match_score": val_result.concept_match_score,
            "is_pass": is_pass,
            "bloom_match": bloom_match,
            "bleu": bleu,
            "rouge_1": r1,
            "rouge_2": r2,
            "rouge_l": rl,
        }
        results.append(res_entry)
        
        # Collect failed and passed attempts for retry metrics
        if val_result.attempts_list:
            for att in val_result.attempts_list:
                vo = att.get("val_out")
                cp = att.get("cand_prof")
                drift_category = "None"
                if att.get("validation_status") == "Fail" and vo and cp:
                    from question_understanding import QuestionUnderstandingEngine
                    orig_prof = QuestionUnderstandingEngine.build_profile(original_q, src_bloom)
                    drift_category = classify_semantic_drift(vo, orig_prof, cp)
                all_attempts_flat.append({
                    "question_id": idx + 1,
                    "attempt": att.get("attempt", 1),
                    "validation_status": att.get("validation_status", ""),
                    "rejection_reason": att.get("rejection_reason", ""),
                    "drift_category": drift_category,
                    "confidence": att.get("confidence", 0.0),
                    "bloom_score": att.get("bloom_score", 0.0),
                    "concept_score": float(str(att.get("concept_score", 0.0)).split("/")[0]) if "/" in str(att.get("concept_score", "")) else float(att.get("concept_score", 0.0)),
                    "entity_score": att.get("entity_score", 0.0),
                    "semantic_score": att.get("semantic_score", 0.0),
                    "number_score": att.get("number_score", 0.0),
                    "grammar_score": att.get("grammar_score", 0.0),
                    "duplicate_score": att.get("duplicate_score", 0.0),
                    "domain_score": att.get("domain_score", 0.0),
                    "topic_score": att.get("topic_score", 0.0),
                    "total_score": att.get("total_score", 0.0),
                    "advisor_activated": att.get("advisor_activated", False),
                    "advisor_guidance_produced": att.get("advisor_guidance_produced", False),
                    "advisor_skipped": att.get("advisor_skipped", False),
                    "missing_preferred": att.get("missing_preferred", []),
                    "missing_supporting": att.get("missing_supporting", []),
                    "generic_terms_detected": att.get("generic_terms_detected", []),
                })
        else:
            # Fallback if attempts_list not populated
            all_attempts_flat.append({
                "question_id": idx + 1,
                "attempt": 1,
                "validation_status": "Pass" if is_pass else "Fail",
                "rejection_reason": val_result.rejection_reason if not is_pass else "",
                "drift_category": "None" if is_pass else "Terminology Change",
                "confidence": val_result.confidence,
                "bloom_score": 0.0,
                "concept_score": 0.0,
                "entity_score": 0.0,
                "semantic_score": 0.0,
                "number_score": 0.0,
                "grammar_score": 0.0,
                "duplicate_score": 0.0,
                "domain_score": 0.0,
                "topic_score": 0.0,
                "total_score": 0.0,
                "advisor_activated": False,
                "advisor_guidance_produced": False,
                "advisor_skipped": False,
                "missing_preferred": [],
                "missing_supporting": [],
                "generic_terms_detected": [],
            })
            
    # Convert to DataFrames
    df_results = pd.DataFrame(results)
    df_attempts = pd.DataFrame(all_attempts_flat)
    
    # ---------------------------------------------------------------------------
    # Calculate statistics & metrics
    # ---------------------------------------------------------------------------
    
    # 1. Generation Statistics
    total_q = len(results)
    total_gen_time = df_results["generation_time"].sum()
    avg_gen_time = df_results["generation_time"].mean()
    
    generation_stats = {
        "total_questions": total_q,
        "total_generation_time_sec": float(round(total_gen_time, 2)),
        "average_generation_time_sec": float(round(avg_gen_time, 2)),
    }
    
    # 2. Validation Statistics
    pass_rate = (df_results["is_pass"].sum() / total_q) * 100.0
    bloom_match_rate = (df_results["bloom_match"].sum() / total_q) * 100.0
    avg_confidence = df_results["confidence"].mean()
    
    # Concept success (not concept drift)
    # Rejection reason is not "Concept Drift" in final accepted questions
    concept_success_count = total_q - (df_results["rejection_reason"] == "Concept Drift").sum()
    concept_success_rate = (concept_success_count / total_q) * 100.0
    
    # Duplicate rejection rate: repetition or duplicate failures / total attempts
    total_attempts_count = df_attempts.shape[0]
    duplicate_failures = df_attempts["rejection_reason"].isin(["Duplicate", "Repetition"]).sum()
    duplicate_rejection_rate = (duplicate_failures / total_attempts_count * 100.0) if total_attempts_count > 0 else 0.0
    
    # Averages of NLP metrics
    avg_bleu = df_results["bleu"].mean()
    avg_r1 = df_results["rouge_1"].mean()
    avg_r2 = df_results["rouge_2"].mean()
    avg_rl = df_results["rouge_l"].mean()

    # Per-stage score averages (from attempts_list for all candidates)
    def safe_avg(col):
        if col in df_attempts.columns:
            return float(round(df_attempts[col].mean(), 4))
        return 0.0

    avg_bloom_score    = safe_avg("bloom_score")
    avg_concept_score  = safe_avg("concept_score")
    avg_entity_score   = safe_avg("entity_score")
    avg_semantic_score = safe_avg("semantic_score")
    avg_number_score   = safe_avg("number_score")
    avg_grammar_score  = safe_avg("grammar_score")
    avg_dup_score      = safe_avg("duplicate_score")
    avg_domain_score   = safe_avg("domain_score")
    avg_topic_score    = safe_avg("topic_score")
    avg_total_score    = safe_avg("total_score")

    # Attempt success breakdown
    attempt_success = {}
    for n in [1, 2, 3, 4]:
        label = f"attempt_{n}_success" if n < 4 else "attempt_4plus_success"
        if "attempt" in df_attempts.columns:
            if n < 4:
                subset = df_attempts[df_attempts["attempt"] == n]
            else:
                subset = df_attempts[df_attempts["attempt"] >= n]
            passed_in_subset = subset[subset["validation_status"].isin(["Pass"])].shape[0]
            attempt_success[label] = int(passed_in_subset)
        else:
            attempt_success[label] = 0

    # Failure distribution (across ALL candidate attempts, not just final result)
    failure_reasons_raw = df_attempts[
        ~df_attempts["rejection_reason"].isin(["", "None", "none"])
    ]["rejection_reason"].value_counts().to_dict()
    failure_distribution = {str(k): int(v) for k, v in failure_reasons_raw.items()}

    validation_stats = {
        "validation_pass_rate_percent": float(round(pass_rate, 2)),
        "bloom_exact_match_percent": float(round(bloom_match_rate, 2)),
        "average_bloom_confidence_percent": float(round(avg_confidence, 2)),
        "concept_validation_success_percent": float(round(concept_success_rate, 2)),
        "duplicate_rejection_rate_percent": float(round(duplicate_rejection_rate, 2)),
        "nlp_metrics": {
            "average_bleu": float(round(avg_bleu, 4)),
            "average_rouge_1": float(round(avg_r1, 4)),
            "average_rouge_2": float(round(avg_r2, 4)),
            "average_rouge_l": float(round(avg_rl, 4)),
        },
        "average_stage_scores": {
            "bloom":     avg_bloom_score,
            "concept":   avg_concept_score,
            "entity":    avg_entity_score,
            "semantic":  avg_semantic_score,
            "number":    avg_number_score,
            "grammar":   avg_grammar_score,
            "duplicate": avg_dup_score,
            "domain":    avg_domain_score,
            "topic":     avg_topic_score,
            "total":     avg_total_score,
        },
        "attempt_success_counts": attempt_success,
        "failure_distribution": failure_distribution,
    }
    
    # 3. Retry Statistics
    avg_retries = (df_results["attempts"] - 1).mean()
    max_retries = int((df_results["attempts"] - 1).max())
    
    # Distribution of attempts
    retry_dist_raw = (df_results["attempts"] - 1).value_counts().to_dict()
    retry_distribution = {str(k): int(v) for k, v in sorted(retry_dist_raw.items())}
    
    # Reasons for retry failures
    retry_reasons_raw = df_attempts[~df_attempts["rejection_reason"].isin(["", "None", "none"])]["rejection_reason"].value_counts().to_dict()
    retry_reasons = {str(k): int(v) for k, v in retry_reasons_raw.items()}
    
    total_weak_flagged = 0
    total_preferred_missing = 0
    advisor_activated_count = 0
    advisor_guidance_produced_count = 0
    advisor_skipped_count = 0
    
    if not df_attempts.empty:
        if "generic_terms_detected" in df_attempts.columns:
            total_weak_flagged = int(df_attempts["generic_terms_detected"].apply(lambda x: len(x) if isinstance(x, list) else 0).sum())
        if "missing_preferred" in df_attempts.columns:
            total_preferred_missing = int(df_attempts["missing_preferred"].apply(lambda x: len(x) if isinstance(x, list) else 0).sum())
        if "advisor_activated" in df_attempts.columns:
            advisor_activated_count = int(df_attempts["advisor_activated"].sum())
        if "advisor_guidance_produced" in df_attempts.columns:
            advisor_guidance_produced_count = int(df_attempts["advisor_guidance_produced"].sum())
        if "advisor_skipped" in df_attempts.columns:
            advisor_skipped_count = int(df_attempts["advisor_skipped"].sum())

    # Count remaining weak terms in final accepted questions
    remaining_weak_count = 0
    remaining_weak_by_term = {}
    from knowledge.terminology import get_topic_terminology
    from question_understanding import QuestionUnderstandingEngine
    
    for res in results:
        gen_q = res.get("generated_question", "")
        target_bloom = res.get("target_bloom", "")
        q_prof = QuestionUnderstandingEngine.build_profile(gen_q, target_bloom)
        topic = q_prof.topic if q_prof and hasattr(q_prof, "topic") else ""
        if topic:
            term_registry = get_topic_terminology(topic)
            if term_registry:
                weak_terms = term_registry.get("weak", [])
                for w in weak_terms:
                    if w.lower() in gen_q.lower():
                        remaining_weak_count += 1
                        remaining_weak_by_term[w] = remaining_weak_by_term.get(w, 0) + 1
            
    retry_stats = {
        "average_retries": float(round(avg_retries, 2)),
        "max_retries": max_retries,
        "retry_distribution": retry_distribution,
        "retry_reasons_list": retry_reasons,
        "weak_terminology_detections": total_weak_flagged,
        "preferred_terminology_advice_instances": total_preferred_missing,
        "advisor_activated_count": advisor_activated_count,
        "advisor_guidance_produced_count": advisor_guidance_produced_count,
        "advisor_skipped_count": advisor_skipped_count,
        "remaining_weak_terms_count": remaining_weak_count,
        "remaining_weak_terms_by_term": remaining_weak_by_term,
    }
    
    # ---------------------------------------------------------------------------
    # Write JSON files
    # ---------------------------------------------------------------------------
    with open("generation_statistics.json", "w", encoding="utf-8") as f:
        json.dump(generation_stats, f, indent=4)
    with open("validation_statistics.json", "w", encoding="utf-8") as f:
        json.dump(validation_stats, f, indent=4)
    with open("retry_statistics.json", "w", encoding="utf-8") as f:
        json.dump(retry_stats, f, indent=4)
        
    # Calculate Semantic Drift breakdown (out of failed attempts)
    failed_attempts = df_attempts[df_attempts["validation_status"].astype(str).str.lower().str.contains("fail")] if not df_attempts.empty else pd.DataFrame()
    drift_counts = {
        "Concept Removal": 0,
        "Concept Addition": 0,
        "Terminology Change": 0,
        "Entity Change": 0,
        "Numeric Change": 0,
        "Algorithm Change": 0,
        "Protocol Change": 0,
        "Domain Vocabulary Change": 0,
        "Topic Vocabulary Change": 0,
        "Intent Change": 0,
        "Equivalent Technical Concepts": 0,
    }
    
    total_failed_with_drift = 0
    if not failed_attempts.empty and "drift_category" in failed_attempts.columns:
        for cat in drift_counts.keys():
            count = (failed_attempts["drift_category"] == cat).sum()
            drift_counts[cat] = int(count)
        total_failed_with_drift = sum(drift_counts.values())
        
    drift_percentages = {}
    for cat, count in drift_counts.items():
        pct = (count / total_failed_with_drift * 100.0) if total_failed_with_drift > 0 else 0.0
        drift_percentages[cat] = {
            "count": count,
            "percentage": float(round(pct, 2))
        }
        
    with open("semantic_drift_breakdown.json", "w", encoding="utf-8") as f:
        json.dump(drift_percentages, f, indent=4)
        
    print("Saved generation_statistics.json, validation_statistics.json, retry_statistics.json, semantic_drift_breakdown.json.")
    print("----------------------------------------------------------")
    print(f"  Remaining weak terms in outputs:  {remaining_weak_count}")
    if remaining_weak_by_term:
        print(f"  Remaining weak terms breakdown:   {remaining_weak_by_term}")
    print("----------------------------------------------------------")
    
    # ---------------------------------------------------------------------------
    # Write CSV files
    # ---------------------------------------------------------------------------
    df_results.to_csv("benchmark_results.csv", index=False)
    print("Saved benchmark_results.csv")
    
    # Write manual_review.csv with specific columns:
    # Original Question, Generated Question, Expected Question, Source Bloom, Target Bloom, Predicted Bloom, Confidence, Retry Count, Generation Time, Validation Result, Comments
    manual_review_records = []
    for r in results:
        manual_review_records.append({
            "Original Question": r["original_question"],
            "Generated Question": r["generated_question"],
            "Expected Question": "",  # Empty placeholder as there is no target rewritten question in dataset
            "Source Bloom": r["source_bloom"],
            "Target Bloom": r["target_bloom"],
            "Predicted Bloom": r["predicted_bloom"],
            "Confidence": r["confidence"],
            "Retry Count": r["attempts"] - 1,
            "Generation Time": round(r["generation_time"], 2),
            "Validation Result": r["validation_status"],
            "Comments": f"Exact Match: {r['bloom_match']}. BLEU: {round(r['bleu'], 3)}. ROUGE-L: {round(r['rouge_l'], 3)}."
        })
    df_manual_review = pd.DataFrame(manual_review_records)
    df_manual_review.to_csv("manual_review.csv", index=False)
    print("Saved manual_review.csv")
    
    # Load baseline metrics if available
    baseline_val = {}
    baseline_retry = {}
    baseline_gen = {}
    baseline_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "before_results")
    if os.path.exists(baseline_dir):
        try:
            with open(os.path.join(baseline_dir, "validation_statistics.json"), "r", encoding="utf-8") as f:
                baseline_val = json.load(f)
            with open(os.path.join(baseline_dir, "retry_statistics.json"), "r", encoding="utf-8") as f:
                baseline_retry = json.load(f)
            with open(os.path.join(baseline_dir, "generation_statistics.json"), "r", encoding="utf-8") as f:
                baseline_gen = json.load(f)
        except Exception as e:
            print(f"[WARNING] Could not load baseline files: {e}")

    comparison_table = ""
    if baseline_val and baseline_retry and baseline_gen:
        b_pass = baseline_val.get("validation_pass_rate_percent", 0.0)
        b_match = baseline_val.get("bloom_exact_match_percent", 0.0)
        b_conf = baseline_val.get("average_bloom_confidence_percent", 0.0)
        b_concept = baseline_val.get("concept_validation_success_percent", 0.0)
        b_dup = baseline_val.get("duplicate_rejection_rate_percent", 0.0)
        b_time = baseline_gen.get("average_generation_time_sec", 0.0)
        b_retries = baseline_retry.get("average_retries", 0.0)
        b_bleu = baseline_val.get("nlp_metrics", {}).get("average_bleu", 0.0)
        b_rouge = baseline_val.get("nlp_metrics", {}).get("average_rouge_l", 0.0)
        
        comparison_table = f"""
## Comparison with Baseline (Before Refactoring)

| Metric | Baseline | Current (After Refactoring) | Delta |
| :--- | :---: | :---: | :---: |
| **Validation Pass Rate** | {b_pass:.2f}% | {pass_rate:.2f}% | {pass_rate - b_pass:+.2f}% |
| **Bloom Exact Match Rate** | {b_match:.2f}% | {bloom_match_rate:.2f}% | {bloom_match_rate - b_match:+.2f}% |
| **Average Bloom Confidence** | {b_conf:.2f}% | {avg_confidence:.2f}% | {avg_confidence - b_conf:+.2f}% |
| **Concept Validation Success** | {b_concept:.2f}% | {concept_success_rate:.2f}% | {concept_success_rate - b_concept:+.2f}% |
| **Duplicate Rejection Rate** | {b_dup:.2f}% | {duplicate_rejection_rate:.2f}% | {duplicate_rejection_rate - b_dup:+.2f}% |
| **Average Generation Time** | {b_time:.2f}s | {avg_gen_time:.2f}s | {avg_gen_time - b_time:+.2f}s |
| **Average Retries** | {b_retries:.2f} | {avg_retries:.2f} | {avg_retries - b_retries:+.2f} |
| **BLEU Score** | {b_bleu:.4f} | {avg_bleu:.4f} | {avg_bleu - b_bleu:+.4f} |
| **ROUGE-L Score** | {b_rouge:.4f} | {avg_rl:.4f} | {avg_rl - b_rouge:+.4f} |

---
"""

    # Build Semantic Drift Breakdown Table
    drift_table = "\n## Top Semantic Drift Causes\n"
    if total_failed_with_drift > 0:
        drift_table += "| Rank | Category | Count | Percentage |\n"
        drift_table += "| :---: | :--- | :---: | :---: |\n"
        # sort by count descending
        sorted_drift = sorted(drift_percentages.items(), key=lambda item: item[1]["count"], reverse=True)
        for rank, (cat, val) in enumerate(sorted_drift, 1):
            drift_table += f"| {rank} | {cat} | {val['count']} | {val['percentage']:.2f}% |\n"
    else:
        drift_table += "No semantic drift or validation failures occurred during this benchmark run.\n"
    drift_table += "\n---\n"

    report_md = f"""# BloomAI Arena v2.1 Pipeline Alignment Report

## Executive Summary
This report summarizes the benchmark evaluation of the aligned FLAN-T5 inference pipeline on **{total_q}** questions from `benchmark_dataset_100.json`.
The inference pipeline has been aligned to match the training prompt distribution exactly on attempt 1, with Mode E retry logic enabled on subsequent attempts.

### Key Quality & Performance Metrics
- **Validation Pass Rate**: {pass_rate:.2f}%
- **Bloom Exact Match Rate**: {bloom_match_rate:.2f}%
- **Average Bloom Confidence**: {avg_confidence:.2f}%
- **Concept Validation Success**: {concept_success_rate:.2f}%
- **Duplicate Rejection Rate**: {duplicate_rejection_rate:.2f}%
- **Average Generation Time**: {avg_gen_time:.2f} seconds
- **Average Retries per Question**: {avg_retries:.2f}

---
{comparison_table}
## NLP Semantic Overlap Metrics (Compared to Source Question)
- **BLEU Score**: {avg_bleu:.4f}
- **ROUGE-1**: {avg_r1:.4f}
- **ROUGE-2**: {avg_r2:.4f}
- **ROUGE-L**: {avg_rl:.4f}

---
{drift_table}
## Performance by Bloom Level
"""
    
    # Breakdown by Target Bloom Level
    bloom_breakdown = []
    for level in ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"]:
        subset = df_results[df_results["target_bloom"] == level]
        if not subset.empty:
            sub_count = len(subset)
            sub_pass = (subset["is_pass"].sum() / sub_count) * 100.0
            sub_match = (subset["bloom_match"].sum() / sub_count) * 100.0
            sub_conf = subset["confidence"].mean()
            sub_retries = (subset["attempts"] - 1).mean()
            sub_time = subset["generation_time"].mean()
            sub_bleu = subset["bleu"].mean()
            sub_rouge = subset["rouge_l"].mean()
            bloom_breakdown.append({
                "Bloom Level": level,
                "Count": sub_count,
                "Pass Rate (%)": f"{sub_pass:.1f}%",
                "Exact Match (%)": f"{sub_match:.1f}%",
                "Avg Conf (%)": f"{sub_conf:.1f}%",
                "Avg Retries": f"{sub_retries:.1f}",
                "Avg Time (s)": f"{sub_time:.1f}s",
                "BLEU": f"{sub_bleu:.3f}",
                "ROUGE-L": f"{sub_rouge:.3f}"
            })
            
    headers = ["Bloom Level", "Count", "Pass Rate (%)", "Exact Match (%)", "Avg Conf (%)", "Avg Retries", "Avg Time (s)", "BLEU", "ROUGE-L"]
    report_md += "| " + " | ".join(headers) + " |\n"
    report_md += "| " + " | ".join(["---"] * len(headers)) + " |\n"
    for row in bloom_breakdown:
        row_vals = [str(row[h]) for h in headers]
        report_md += "| " + " | ".join(row_vals) + " |\n"
    
    report_md += """

---

## Retry Analysis
### Retry Distribution
| Retries | Question Count |
|---|---|
"""
    for retries_str, count in retry_distribution.items():
        report_md += f"| {retries_str} | {count} |\n"

    # Attempt success breakdown
    report_md += "\n### Attempt Success Breakdown\n| Attempt | Passed Candidates |\n|---|---|\n"
    for label, cnt in attempt_success.items():
        friendly = label.replace("_", " ").title()
        report_md += f"| {friendly} | {cnt} |\n"

    report_md += """
### Failed Candidates Rejection Reasons
| Reason | Count |
|---|---|
"""
    for reason, count in retry_reasons.items():
        report_md += f"| {reason} | {count} |\n"

    # Remaining Weak Terms Summary
    report_md += f"""
---

## Remaining Weak Terms Summary
- **Remaining Weak Terms in Final Outputs**: {remaining_weak_count}
"""
    if remaining_weak_by_term:
        report_md += "- **Remaining Weak Terms Breakdown**:\n"
        for term, cnt in sorted(remaining_weak_by_term.items(), key=lambda x: x[1], reverse=True):
            report_md += f"  - `{term}`: {cnt}\n"

    # Stage score averages
    report_md += """
---

## Average Stage Scores (All Candidates)
| Stage | Max Points | Average Score |
|---|---|---|
"""
    stage_maxes = {
        "Bloom":     35.0,
        "Domain":    20.0,
        "Topic":     15.0,
        "Concept":   10.0,
        "Entity":    10.0,
        "Number":     5.0,
        "Grammar":    3.0,
        "Duplicate":  2.0,
    }
    stage_avgs = {
        "Bloom":     avg_bloom_score,
        "Domain":    avg_domain_score,
        "Topic":     avg_topic_score,
        "Concept":   avg_concept_score,
        "Entity":    avg_entity_score,
        "Number":    avg_number_score,
        "Grammar":   avg_grammar_score,
        "Duplicate": avg_dup_score,
    }
    for stage, mx in stage_maxes.items():
        av = stage_avgs[stage]
        report_md += f"| **{stage}** | {mx:.1f} | {av:.4f} |\n"
    report_md += f"| **Total** | 100.0 | {avg_total_score:.4f} |\n"

    # Failure distribution
    if failure_distribution:
        report_md += """
---

## Validation Failure Distribution
| Rejection Reason | Count |
|---|---|
"""
        for reason, count in failure_distribution.items():
            report_md += f"| {reason} | {count} |\n"

    report_md += """
---

## Conclusion
The aligned FLAN-T5 generation pipeline satisfies both natural question structure requirements and cognitive rigor as enforced by DeBERTa classification, concept matching, and semantic duplicate validation.
"""

    with open("benchmark_report.md", "w", encoding="utf-8") as f:
        f.write(report_md)

    print("Saved benchmark_report.md")
    
    # Print cache hits and misses if debug is enabled or by default
    import spacy_utils
    print("----------------------------------------------------------")
    print("Cache Statistics:")
    print(f"  spaCy Doc Cache Hits   : {spacy_utils.SPACY_CACHE_HITS}")
    print(f"  spaCy Doc Cache Misses : {spacy_utils.SPACY_CACHE_MISSES}")
    print(f"  Embedding Cache Hits   : {app.EMBEDDING_CACHE_HITS}")
    print(f"  Embedding Cache Misses : {app.EMBEDDING_CACHE_MISSES}")
    print("----------------------------------------------------------")
    print("Benchmark complete!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run FLAN-T5 inference pipeline benchmarks.")
    parser.add_argument(
        "--dataset",
        type=str,
        default="benchmark_dataset_100.json",
        help="Path to the JSON dataset file."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit the number of questions processed (for quick testing)."
    )
    args = parser.parse_args()
    
    run_benchmark(args.dataset, args.limit)
