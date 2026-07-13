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
    classify_text,
    extract_core_phrase,
    generate_validated_variant,
    infer_domain,
    BLOOM_TO_DIFFICULTY,
)
from config import MODES

BLOOM_LEVELS = ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"]


def load_benchmark_questions():
    csv_path = os.path.join(os.path.dirname(__file__), "benchmark_questions.csv")
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        if "Question" in df.columns:
            return df["Question"].tolist()

    # Fallback to standard 5 questions
    print(f"Warning: {csv_path} not found or missing 'Question' column. Using fallback.")
    return [
        "Explain the concept of ACID properties in a relational database management system.",
        "Describe the process of database normalization and its role in reducing data redundancy.",
        "How does a B-tree index improve the performance of SQL SELECT queries?",
        "Discuss the trade-offs between using a NoSQL database versus a traditional relational database.",
        "What is a database transaction, and how do commit and rollback operations work?"
    ]


REQUIRED_JSON_FIELDS = {"question", "expected_bloom", "expected_difficulty", "domain", "topic"}


def load_json_dataset(path: str):
    """Load a structured JSON benchmark dataset.

    Returns a list of dicts, each with keys:
        question, expected_bloom, expected_difficulty, domain, topic

    Raises SystemExit if required fields are missing in any record.
    """
    abs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), path)
    if not os.path.exists(abs_path):
        print(f"[ERROR] Dataset file not found: {abs_path}")
        sys.exit(1)

    with open(abs_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    errors = []
    for idx, rec in enumerate(records):
        missing = REQUIRED_JSON_FIELDS - set(rec.keys())
        if missing:
            errors.append(f"  Record {idx + 1}: missing fields {sorted(missing)!r}")

    if errors:
        print("[ERROR] Dataset is missing required fields:")
        for e in errors:
            print(e)
        sys.exit(1)

    print(f"Loaded JSON dataset: {os.path.basename(abs_path)} ({len(records)} records)")
    return records


def compute_semantic_similarity(q1, q2):
    st = app._get_st_model()
    if st is None or not q1 or not q2:
        return 0.0
    try:
        emb1 = app.get_cached_embedding(q1, st)
        emb2 = app.get_cached_embedding(q2, st)
        sim = float(torch.nn.functional.cosine_similarity(emb1.unsqueeze(0), emb2.unsqueeze(0)).item())
        return round(sim, 4)
    except Exception as e:
        print(f"Error computing similarity: {e}")
        return 0.0


def bloom_precision_recall_f1(df, target_col="Target Bloom", pred_col="Predicted Bloom"):
    results = {}
    for level in BLOOM_LEVELS:
        tp = ((df[target_col] == level) & (df[pred_col] == level)).sum()
        fp = ((df[target_col] != level) & (df[pred_col] == level)).sum()
        fn = ((df[target_col] == level) & (df[pred_col] != level)).sum()
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (
            2 * precision * recall / (precision + recall)
            if (precision + recall) > 0
            else 0.0
        )
        results[level] = {
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "f1": round(f1, 3),
        }
    return results


def determine_winner(b_pass, e_pass, b_bloom_ok, e_bloom_ok, b_sim, e_sim, b_conf, e_conf, b_attempts, e_attempts):
    # Rule 1: One passes, the other fails
    if b_pass and not e_pass:
        return "Mode B", "Mode B passed validation while Mode E failed."
    if e_pass and not b_pass:
        return "Mode E", "Mode E passed validation while Mode B failed."
    
    # Rule 2: Both passed
    if b_pass and e_pass:
        if b_bloom_ok and not e_bloom_ok:
            return "Mode B", "Mode B predicted Bloom matches target; Mode E does not."
        if e_bloom_ok and not b_bloom_ok:
            return "Mode E", "Mode E predicted Bloom matches target; Mode B does not."
        
        # Lower attempts (FLAN calls) is better
        if b_attempts < e_attempts:
            return "Mode B", f"Mode B succeeded in fewer attempts ({b_attempts} vs {e_attempts})."
        if e_attempts < b_attempts:
            return "Mode E", f"Mode E succeeded in fewer attempts ({e_attempts} vs {b_attempts})."
            
        # Higher semantic similarity is better
        if e_sim - b_sim > 0.02:
            return "Mode E", f"Mode E has higher semantic similarity ({e_sim:.4f} vs {b_sim:.4f})."
        if b_sim - e_sim > 0.02:
            return "Mode B", f"Mode B has higher semantic similarity ({b_sim:.4f} vs {e_sim:.4f})."
            
        # Higher confidence is better
        if e_conf > b_conf:
            return "Mode E", f"Mode E has higher classifier confidence ({e_conf:.2f}% vs {b_conf:.2f}%)."
        if b_conf > e_conf:
            return "Mode B", f"Mode B has higher classifier confidence ({b_conf:.2f}% vs {e_conf:.2f}%)."
        
        return "Tie", "Both modes performed equally well on all metrics."

    # Rule 3: Both failed
    if b_bloom_ok and not e_bloom_ok:
        return "Mode B", "Both failed, but Mode B predicted Bloom matches target."
    if e_bloom_ok and not b_bloom_ok:
        return "Mode E", "Both failed, but Mode E predicted Bloom matches target."
    
    if e_sim > b_sim:
        return "Mode E", "Both failed, but Mode E has higher semantic similarity."
    if b_sim > e_sim:
        return "Mode B", "Both failed, but Mode B has higher semantic similarity."
        
    return "Tie", "Both modes failed and had similar metrics."


def get_starting_verb(question):
    words = re.findall(r"\b\w+\b", question.strip().lower())
    return words[0] if words else ""


def parse_frac(val):
    if isinstance(val, str) and "/" in val:
        try:
            n, d = val.split("/")
            return float(n) / float(d) if float(d) else 0
        except Exception:
            return 0
    try:
        return float(val)
    except Exception:
        return 0


def save_dataframe(df, filename):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    df.to_csv(os.path.join(script_dir, filename), index=False)
    
    cwd = os.getcwd()
    if os.path.abspath(cwd) != os.path.abspath(script_dir):
        df.to_csv(os.path.join(cwd, filename), index=False)


def save_text(text, filename):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(script_dir, filename), "w", encoding="utf-8") as f:
        f.write(text)
    
    cwd = os.getcwd()
    if os.path.abspath(cwd) != os.path.abspath(script_dir):
        with open(os.path.join(cwd, filename), "w", encoding="utf-8") as f:
            f.write(text)


def run_benchmark(dataset_path: str = None, model_version: str = "v9"):
    print("==================================================")
    print(f"Initializing BloomAI Arena Experiment Pipeline (Model: {model_version})")
    print("==================================================")

    print("Loading model checkpoints sequentially...")
    load_models()
    print("Models loaded successfully.")

    # ----------------------------------------------------------------
    # Dataset loading — default behaviour preserved when no --dataset
    # ----------------------------------------------------------------
    json_dataset = None
    if dataset_path:
        json_dataset = load_json_dataset(dataset_path)
        questions = [rec["question"] for rec in json_dataset]
        print(f"Running extended benchmark: {dataset_path} ({len(questions)} questions)")
    else:
        questions = load_benchmark_questions()
        print(f"Loaded {len(questions)} source questions for evaluation.")

    eval_results = []
    first_attempt_results = []
    failure_analysis_results = []
    runs_map = {}

    modes_to_evaluate = ["Mode B (Production)", "Mode E (Multi-Candidate Ranking)"]

    for mode_name in modes_to_evaluate:
        print(f"\nEvaluating mode: {mode_name}")
        config_mode = MODES[mode_name]
        # Build an iterable of (question, target_bloom, target_difficulty, domain_hint, topic_hint)
        # For the JSON dataset each question has one pre-labelled target.
        # For the default CSV dataset we iterate all Bloom levels (existing behaviour).
        if json_dataset is not None:
            # Build a question->record lookup (by exact text)
            q_to_rec = {rec["question"]: rec for rec in json_dataset}

        for original_q in tqdm(questions, desc=f"Running {mode_name}"):
            src_bloom, src_diff, _ = classify_text(original_q)
            extracted_concept = extract_core_phrase(original_q)
            domain = infer_domain(original_q, extracted_concept)

            if json_dataset is not None:
                # Single target per question from the dataset record
                rec = q_to_rec.get(original_q, {})
                bloom_iter = [(rec.get("expected_bloom", src_bloom),
                               rec.get("expected_difficulty", src_diff))]
            else:
                # Default: all Bloom levels (existing behaviour unchanged)
                bloom_iter = [(tb, BLOOM_TO_DIFFICULTY.get(tb, "Medium")) for tb in BLOOM_LEVELS]

            for t_bloom, t_diff in bloom_iter:
                session_seen = []

                candidate = generate_validated_variant(
                    question=original_q,
                    src_bloom=src_bloom,
                    src_diff=src_diff,
                    target_bloom=t_bloom,
                    target_difficulty=t_diff,
                    domain=domain,
                    required_concept=extracted_concept,
                    session_seen=session_seen,
                    config_mode=config_mode,
                    mode_name=mode_name,
                    model_version=model_version,
                )

                is_pass = candidate.validation_status in ["Pass", "Exact Match", "Adjacent Match"]
                sim_score = compute_semantic_similarity(candidate.generated_question, original_q)

                result_entry = {
                    "Mode": mode_name,
                    "Source Question": original_q,
                    "Extracted Concept": extracted_concept,
                    "Generated Question": candidate.generated_question,
                    "Target Bloom": t_bloom,
                    "Predicted Bloom": candidate.predicted_bloom,
                    "Target Difficulty": t_diff,
                    "Predicted Difficulty": candidate.predicted_difficulty,
                    "Confidence": candidate.confidence,
                    "Rejection Reason": candidate.rejection_reason,
                    "Concept Match Score": candidate.concept_match_score,
                    "Attempts": candidate.attempts,
                    "Generation Time": round(candidate.generation_time, 2),
                    "Overall Pass": "Pass" if is_pass else "Fail",
                    "Prompt Used": candidate.prompt_used,
                    "Prompt Tokens": candidate.prompt_tokens,
                    "Completion Tokens": candidate.completion_tokens,
                    "Total Tokens": candidate.prompt_tokens + candidate.completion_tokens,
                    "Semantic Similarity": sim_score,
                    
                    "Flan Calls": getattr(candidate, "flan_calls", candidate.attempts),
                    "Deberta Calls": getattr(candidate, "deberta_calls", candidate.attempts),
                    "Candidates Generated": getattr(candidate, "candidates_generated", candidate.attempts),
                    "Candidates Validated": getattr(candidate, "candidates_validated", candidate.attempts),
                    "Candidates Rejected Before Validation": getattr(candidate, "candidates_rejected_before_validation", 0),
                }
                
                eval_results.append(result_entry)
                runs_map[(original_q, t_bloom, t_diff, mode_name)] = result_entry

                # First Attempt Analysis
                first_att = candidate.attempts_list[0] if candidate.attempts_list else None
                first_attempt_entry = {
                    "Source Question": original_q,
                    "Mode": mode_name,
                    "Accepted First Attempt": "Yes" if (first_att and first_att.get("validation_status") == "Pass") else "No",
                    "Attempt Count": candidate.attempts,
                    "Failure Reason": first_att.get("rejection_reason", "N/A") if first_att else "No Attempt",
                    "Generation Time": round(first_att.get("generation_time", 0.0), 4) if first_att else 0.0,
                }
                first_attempt_results.append(first_attempt_entry)

                # Failure Analysis
                for att in (candidate.attempts_list or []):
                    if att.get("validation_status") == "Fail":
                        fail_sim = compute_semantic_similarity(att.get("generated_question"), original_q)
                        fail_entry = {
                            "Source Question": original_q,
                            "Generated Question": att.get("generated_question"),
                            "Target Bloom": t_bloom,
                            "Predicted Bloom": att.get("bloom_prediction"),
                            "Target Difficulty": t_diff,
                            "Predicted Difficulty": att.get("difficulty_prediction"),
                            "Confidence": att.get("confidence", 0.0),
                            "Concept Match": att.get("concept_score"),
                            "Semantic Similarity": fail_sim,
                            "Duplicate Score": att.get("duplicate_score", 0.0),
                            "Failure Reason": att.get("rejection_reason"),
                            "Attempt Number": att.get("attempt"),
                            "Starting Verb": get_starting_verb(att.get("generated_question")),
                            "Prompt Version": "Multi-Candidate Ranking" if "Mode E" in mode_name else "Production Baseline",
                        }
                        failure_analysis_results.append(fail_entry)

    df_eval = pd.DataFrame(eval_results)
    save_dataframe(df_eval, "evaluation_results.csv")
    print("Saved evaluation_results.csv")

    df_first = pd.DataFrame(first_attempt_results)
    save_dataframe(df_first, "first_attempt_analysis.csv")
    print("Saved first_attempt_analysis.csv")

    df_failure = pd.DataFrame(failure_analysis_results)
    save_dataframe(df_failure, "failure_analysis.csv")
    print("Saved failure_analysis.csv")

    prompt_stats_list = []
    for m_name in modes_to_evaluate:
        m_runs = [r for r in eval_results if r["Mode"] == m_name]
        version = "Multi-Candidate Ranking" if "Mode E" in m_name else "Production Baseline"
        
        prompts = [r["Prompt Used"] for r in m_runs if r["Prompt Used"]]
        completions = [r["Generated Question"] for r in m_runs if r["Generated Question"]]
        
        avg_prompt_len = sum(len(p) for p in prompts) / len(prompts) if prompts else 0
        avg_resp_len = sum(len(c) for c in completions) / len(completions) if completions else 0
        
        avg_prompt_tok = sum(r["Prompt Tokens"] for r in m_runs) / len(m_runs) if m_runs else 0
        avg_comp_tok = sum(r["Completion Tokens"] for r in m_runs) / len(m_runs) if m_runs else 0
        avg_total_tok = avg_prompt_tok + avg_comp_tok
        
        prompt_stats_list.append({
            "Mode": m_name,
            "Prompt Version": version,
            "Prompt Length": round(avg_prompt_len, 1),
            "Prompt Tokens": round(avg_prompt_tok, 1),
            "Completion Tokens": round(avg_comp_tok, 1),
            "Total Tokens": round(avg_total_tok, 1),
            "Average Response Length": round(avg_resp_len, 1)
        })
    df_prompt_stats = pd.DataFrame(prompt_stats_list)
    save_dataframe(df_prompt_stats, "prompt_statistics.csv")
    print("Saved prompt_statistics.csv")

    gen_comparison_list = []
    manual_review_list = []

    for q in questions:
        for tb in BLOOM_LEVELS:
            td = BLOOM_TO_DIFFICULTY.get(tb, "Medium")
            
            run_b = runs_map.get((q, tb, td, "Mode B (Production)"))
            run_e = runs_map.get((q, tb, td, "Mode E (Multi-Candidate Ranking)"))
            
            if run_b and run_e:
                b_pass = run_b["Overall Pass"] == "Pass"
                e_pass = run_e["Overall Pass"] == "Pass"
                b_bloom_ok = run_b["Predicted Bloom"] == tb
                e_bloom_ok = run_e["Predicted Bloom"] == tb
                
                winner, reason = determine_winner(
                    b_pass, e_pass, b_bloom_ok, e_bloom_ok,
                    run_b["Semantic Similarity"], run_e["Semantic Similarity"],
                    run_b["Confidence"], run_e["Confidence"],
                    run_b["Attempts"], run_e["Attempts"]
                )
                
                gen_comparison_list.append({
                    "Source Question": q,
                    "Target Bloom": tb,
                    "Target Difficulty": td,
                    "Mode B Output": run_b["Generated Question"],
                    "Mode E Output": run_e["Generated Question"],
                    "Mode B Prediction": run_b["Predicted Bloom"],
                    "Mode E Prediction": run_e["Predicted Bloom"],
                    "Concept Score": run_e["Concept Match Score"],
                    "Semantic Similarity": run_e["Semantic Similarity"],
                    "Winner": winner,
                    "Reason": reason
                })
                
                manual_review_list.append({
                    "Source Question": q,
                    "Mode B Output": run_b["Generated Question"],
                    "Mode E Output": run_e["Generated Question"],
                    "Target Bloom": tb,
                    "Target Difficulty": td,
                    "Concept": run_b["Extracted Concept"],
                    "Human Winner": winner if winner in ["Mode B", "Mode E"] else "Tie",
                    "Reviewer Notes": f"Auto Winner: {winner}. Reason: {reason}"
                })

    df_gen_comp = pd.DataFrame(gen_comparison_list)
    save_dataframe(df_gen_comp, "generation_comparison.csv")
    print("Saved generation_comparison.csv")

    df_man = pd.DataFrame(manual_review_list)
    save_dataframe(df_man, "manual_review.csv")
    print("Saved manual_review.csv")

    comparison_stats = []
    for mode_name in modes_to_evaluate:
        m_runs = df_eval[df_eval["Mode"] == mode_name]
        total = len(m_runs)
        passed_df = m_runs[m_runs["Overall Pass"] == "Pass"]
        total_passed = len(passed_df)

        bloom_accuracy = (m_runs["Target Bloom"] == m_runs["Predicted Bloom"]).sum() / total * 100
        diff_accuracy = (m_runs["Target Difficulty"] == m_runs["Predicted Difficulty"]).sum() / total * 100
        concept_preservation = (m_runs["Rejection Reason"] != "Concept Drift").sum() / total * 100
        duplicate_rate = (m_runs["Rejection Reason"] == "Duplicate").sum() / total * 100
        failure_rate = (total - total_passed) / total * 100
        overall_pass_rate = total_passed / total * 100
        
        first_att_ok = sum(1 for r in first_attempt_results if r["Mode"] == mode_name and r["Accepted First Attempt"] == "Yes")
        first_attempt_success_rate = first_att_ok / total * 100
        
        second_att_ok = sum(1 for r in eval_results if r["Mode"] == mode_name and r["Overall Pass"] == "Pass" and r["Attempts"] == 2)
        second_attempt_success_rate = second_att_ok / total * 100
        
        accepted_retry_ok = sum(1 for r in eval_results if r["Mode"] == mode_name and r["Overall Pass"] == "Pass" and r["Attempts"] > 1)
        accepted_after_retry = accepted_retry_ok / total * 100
        
        failed_retry_ok = sum(1 for r in eval_results if r["Mode"] == mode_name and r["Overall Pass"] == "Fail" and r["Attempts"] > 1)
        failed_after_retry = failed_retry_ok / total * 100
        
        avg_conf = passed_df["Confidence"].mean() if total_passed > 0 else 0
        avg_time = passed_df["Generation Time"].mean() if total_passed > 0 else 0
        avg_attempts = m_runs["Attempts"].mean() if total > 0 else 0
        avg_sim = m_runs["Semantic Similarity"].mean() if total > 0 else 0

        avg_flan_calls = m_runs["Flan Calls"].mean() if "Flan Calls" in m_runs.columns else avg_attempts
        avg_deberta_calls = m_runs["Deberta Calls"].mean() if "Deberta Calls" in m_runs.columns else avg_attempts
        avg_generated = m_runs["Candidates Generated"].mean() if "Candidates Generated" in m_runs.columns else avg_attempts
        avg_validated = m_runs["Candidates Validated"].mean() if "Candidates Validated" in m_runs.columns else avg_attempts
        avg_rejected_before = m_runs["Candidates Rejected Before Validation"].mean() if "Candidates Rejected Before Validation" in m_runs.columns else 0

        prf = bloom_precision_recall_f1(m_runs)
        macro_f1 = sum(prf[lv]["f1"] for lv in BLOOM_LEVELS) / len(BLOOM_LEVELS)

        comparison_stats.append({
            "Mode": mode_name,
            "First Attempt Success Rate (%)": round(first_attempt_success_rate, 1),
            "Second Attempt Success Rate (%)": round(second_attempt_success_rate, 1),
            "Accepted After Retry (%)": round(accepted_after_retry, 1),
            "Failed After Retry (%)": round(failed_after_retry, 1),
            "Overall Pass Rate (%)": round(overall_pass_rate, 1),
            "Bloom Accuracy (%)": round(bloom_accuracy, 1),
            "Difficulty Accuracy (%)": round(diff_accuracy, 1),
            "Bloom Macro F1": round(macro_f1, 3),
            "Concept Preservation (%)": round(concept_preservation, 1),
            "Semantic Similarity": round(avg_sim, 4),
            "Average Confidence (%)": round(avg_conf, 1),
            "Average Retries": round(avg_attempts, 2),
            "Average Generation Time (s)": round(avg_time, 2),
            "Duplicate Rate (%)": round(duplicate_rate, 1),
            "Failure Rate (%)": round(failure_rate, 1),
            "Average FLAN Calls": round(avg_flan_calls, 2),
            "Average DeBERTa Calls": round(avg_deberta_calls, 2),
            "Average Candidates Generated": round(avg_generated, 2),
            "Average Candidates Validated": round(avg_validated, 2),
            "Average Candidates Rejected Before Validation": round(avg_rejected_before, 2),
        })

    df_comp = pd.DataFrame(comparison_stats)
    save_dataframe(df_comp, "benchmark_prompt_comparison.csv")
    print("Saved benchmark_prompt_comparison.csv")

    generate_mode_e_markdown_report(df_eval, comparison_stats, failure_analysis_results, df_prompt_stats, df_first, df_gen_comp)

    # Extended 100-question report when a JSON dataset is used
    if json_dataset is not None:
        generate_benchmark_100_report(df_eval, json_dataset, comparison_stats, failure_analysis_results)


def generate_mode_e_markdown_report(df_eval, comparison_stats, failure_analysis_results, df_prompt_stats, df_first, df_gen_comp):
    b_stats = next(s for s in comparison_stats if s["Mode"] == "Mode B (Production)")
    e_stats = next(s for s in comparison_stats if s["Mode"] == "Mode E (Multi-Candidate Ranking)")
    
    bloom_ok = e_stats["Bloom Accuracy (%)"] >= b_stats["Bloom Accuracy (%)"]
    diff_ok = e_stats["Difficulty Accuracy (%)"] >= b_stats["Difficulty Accuracy (%)"]
    pass_rate_ok = e_stats["Overall Pass Rate (%)"] >= b_stats["Overall Pass Rate (%)"]
    concept_ok = e_stats["Concept Preservation (%)"] >= b_stats["Concept Preservation (%)"]
    first_attempt_ok = e_stats["First Attempt Success Rate (%)"] >= b_stats["First Attempt Success Rate (%)"]
    
    time_target = b_stats["Average Generation Time (s)"] * 0.80
    time_ok = e_stats["Average Generation Time (s)"] <= time_target
    flan_calls_ok = e_stats["Average FLAN Calls"] < b_stats["Average FLAN Calls"]
    fail_rate_ok = e_stats["Failure Rate (%)"] <= b_stats["Failure Rate (%)"]
    
    all_success_criteria_met = (
        bloom_ok and diff_ok and pass_rate_ok and concept_ok and
        first_attempt_ok and time_ok and flan_calls_ok and fail_rate_ok
    )
    
    lines = []
    lines.append("# BloomAI Arena v2.1 Mode E Evaluation Report")
    lines.append("")
    lines.append("## Executive Summary")
    lines.append("")
    lines.append("This report evaluates the performance of **Mode E (Multi-Candidate Ranking)** against the production baseline **Mode B (Production)**. Mode E introduces a multi-candidate generation strategy returning up to 5 candidates per FLAN-T5 call and performing ranking-based selection, whereas Mode B runs a sequential retry-until-success strategy. Both modes are evaluated on identical questions, templates, validation parameters, and models.")
    lines.append("")
    
    if all_success_criteria_met:
        lines.append("> [!IMPORTANT]")
        lines.append("> **Recommendation:** **PROMOTE TO PRODUCTION**. Mode E meets all adoption success criteria, showing significant latency reduction and call efficiency without sacrificing quality.")
    else:
        lines.append("> [!WARNING]")
        lines.append("> **Recommendation:** **REJECT OR REWRITE**. Mode E failed to meet one or more success criteria. Do not promote Mode E to production default without addressing the failures.")
    lines.append("")
    
    lines.append("## Adoption Success Criteria Checklist")
    lines.append("")
    
    def check_line(label, condition, val_e, val_b, fmt="{:.1f}%"):
        status = "✅ MET" if condition else "❌ FAILED"
        lines.append(f"- **{label}:** {status} (Mode E: {fmt.format(val_e)} vs Mode B: {fmt.format(val_b)})")
        
    check_line("Bloom Accuracy (>= Mode B)", bloom_ok, e_stats["Bloom Accuracy (%)"], b_stats["Bloom Accuracy (%)"])
    check_line("Difficulty Accuracy (>= Mode B)", diff_ok, e_stats["Difficulty Accuracy (%)"], b_stats["Difficulty Accuracy (%)"])
    check_line("Overall Pass Rate (>= Mode B)", pass_rate_ok, e_stats["Overall Pass Rate (%)"], b_stats["Overall Pass Rate (%)"])
    check_line("Concept Preservation (>= Mode B)", concept_ok, e_stats["Concept Preservation (%)"], b_stats["Concept Preservation (%)"])
    check_line("First Attempt Success Rate (>= Mode B)", first_attempt_ok, e_stats["First Attempt Success Rate (%)"], b_stats["First Attempt Success Rate (%)"])
    check_line("Average Generation Time (>= 20% lower)", time_ok, e_stats["Average Generation Time (s)"], b_stats["Average Generation Time (s)"], "{:.2f}s")
    check_line("Average FLAN Calls (lower than Mode B)", flan_calls_ok, e_stats["Average FLAN Calls"], b_stats["Average FLAN Calls"], "{:.2f}")
    check_line("Failure Rate (does not increase)", fail_rate_ok, e_stats["Failure Rate (%)"], b_stats["Failure Rate (%)"])
    
    lines.append("")
    lines.append("## Detailed Metric Comparison Table")
    lines.append("")
    lines.append("| Metric | Mode B (Production) | Mode E (Multi-Candidate) | Difference | Status |")
    lines.append("|---|---|---|---|---|")
    
    def add_row_detail(name, key, is_f1=False):
        val_b = b_stats[key]
        val_e = e_stats[key]
        diff = val_e - val_b
        
        diff_sign = "+" if diff >= 0 else ""
        diff_str = f"{diff_sign}{diff:.3f}" if is_f1 else f"{diff_sign}{diff:.2f}"
        if "%" in key:
            diff_str += "%"
            
        if key == "Failure Rate (%)":
            pass_cond = diff <= 0
        elif key == "Average Generation Time (s)":
            pass_cond = val_e <= (val_b * 0.80)
        elif key == "Average FLAN Calls":
            pass_cond = val_e < val_b
        else:
            pass_cond = diff >= 0
            
        status = "PASS" if pass_cond else "FAIL"
        lines.append(f"| {name} | {val_b} | {val_e} | {diff_str} | {status} |")
        
    add_row_detail("First Attempt Success Rate", "First Attempt Success Rate (%)")
    add_row_detail("Second Attempt Success Rate", "Second Attempt Success Rate (%)")
    add_row_detail("Accepted After Retry", "Accepted After Retry (%)")
    add_row_detail("Failed After Retry", "Failed After Retry (%)")
    add_row_detail("Overall Pass Rate", "Overall Pass Rate (%)")
    add_row_detail("Bloom Accuracy", "Bloom Accuracy (%)")
    add_row_detail("Difficulty Accuracy", "Difficulty Accuracy (%)")
    add_row_detail("Bloom Macro F1", "Bloom Macro F1", is_f1=True)
    add_row_detail("Concept Preservation", "Concept Preservation (%)")
    add_row_detail("Average Confidence", "Average Confidence (%)")
    add_row_detail("Average FLAN Calls", "Average FLAN Calls")
    add_row_detail("Average Generation Time (s)", "Average Generation Time (s)")
    add_row_detail("Duplicate Rate", "Duplicate Rate (%)")
    add_row_detail("Failure Rate", "Failure Rate (%)")
    
    lines.append("")
    lines.append("## Mode E Execution Call Statistics")
    lines.append("")
    lines.append("These metrics track candidates processed in the pipeline:")
    lines.append(f"- **Average Candidates Generated per Variant:** {e_stats['Average Candidates Generated']:.2f}")
    lines.append(f"- **Average Candidates Validated (DeBERTa Calls) per Variant:** {e_stats['Average Candidates Validated']:.2f}")
    lines.append(f"- **Average Candidates Deduplicated (Rejected Before Validation) per Variant:** {e_stats['Average Candidates Rejected Before Validation']:.2f}")
    lines.append("")
    
    lines.append("## Bloom-Level Performance Analysis")
    lines.append("")
    lines.append("### Per-Bloom Level Accuracy Comparison")
    lines.append("| Bloom Level | Mode B Accuracy | Mode E Accuracy | Difference |")
    lines.append("|---|---|---|---|")
    
    for lvl in BLOOM_LEVELS:
        b_sub = df_eval[(df_eval["Mode"] == "Mode B (Production)") & (df_eval["Target Bloom"] == lvl)]
        b_acc = (b_sub["Predicted Bloom"] == lvl).sum() / len(b_sub) * 100 if len(b_sub) > 0 else 0
        
        e_sub = df_eval[(df_eval["Mode"] == "Mode E (Multi-Candidate Ranking)") & (df_eval["Target Bloom"] == lvl)]
        e_acc = (e_sub["Predicted Bloom"] == lvl).sum() / len(e_sub) * 100 if len(e_sub) > 0 else 0
        
        lines.append(f"| {lvl} | {b_acc:.1f}% | {e_acc:.1f}% | {(e_acc - b_acc):+.1f}% |")
    lines.append("")
    
    lines.append("### Transformation Pair Analysis")
    lines.append("This section tracks how questions migrate across cognitive transitions. Below are the pass rates for specific Bloom level target mappings:")
    lines.append("")
    lines.append("| Transition | Mode B Pass Rate | Mode E Pass Rate | Difference |")
    lines.append("|---|---|---|---|")
    
    trans_pairs = []
    for sb in BLOOM_LEVELS:
        for tb in BLOOM_LEVELS:
            if sb != tb:
                trans_pairs.append((sb, tb))
                
    for sb, tb in trans_pairs:
        b_pair = df_eval[(df_eval["Mode"] == "Mode B (Production)") & (df_eval["Target Bloom"] == tb)]
        b_pair_pass = (b_pair["Overall Pass"] == "Pass").sum() / len(b_pair) * 100 if len(b_pair) > 0 else 0
        
        e_pair = df_eval[(df_eval["Mode"] == "Mode E (Multi-Candidate Ranking)") & (df_eval["Target Bloom"] == tb)]
        e_pair_pass = (e_pair["Overall Pass"] == "Pass").sum() / len(e_pair) * 100 if len(e_pair) > 0 else 0
        
        lines.append(f"| {sb} &rarr; {tb} | {b_pair_pass:.1f}% | {e_pair_pass:.1f}% | {(e_pair_pass - b_pair_pass):+.1f}% |")
    lines.append("")
    
    lines.append("## Rejection Reason Distribution")
    lines.append("")
    lines.append("| Rejection Reason | Mode B Count | Mode E Count | Mode B % | Mode E % |")
    lines.append("|---|---|---|---|---|")
    
    b_fails = df_eval[(df_eval["Mode"] == "Mode B (Production)") & (df_eval["Overall Pass"] == "Fail")]
    e_fails = df_eval[(df_eval["Mode"] == "Mode E (Multi-Candidate Ranking)") & (df_eval["Overall Pass"] == "Fail")]
    
    reasons = set(b_fails["Rejection Reason"].unique()) | set(e_fails["Rejection Reason"].unique())
    reasons = {r for r in reasons if r and r != "None" and r != "N/A"}
    
    for r in sorted(reasons):
        b_count = (b_fails["Rejection Reason"] == r).sum()
        e_count = (e_fails["Rejection Reason"] == r).sum()
        b_pct = b_count / len(b_fails) * 100 if len(b_fails) > 0 else 0
        e_pct = e_count / len(e_fails) * 100 if len(e_fails) > 0 else 0
        lines.append(f"| {r} | {b_count} | {e_count} | {b_pct:.1f}% | {e_pct:.1f}% |")
    lines.append("")
    
    lines.append("## Prompt Cost Analysis")
    lines.append("")
    lines.append("| Mode | Prompt Tokens | Completion Tokens | Total Tokens | Cost Factor |")
    lines.append("|---|---|---|---|---|")
    for _, row in df_prompt_stats.iterrows():
        cost_factor = round(row["Total Tokens"] / df_prompt_stats.iloc[0]["Total Tokens"], 2)
        lines.append(f"| {row['Mode']} | {row['Prompt Tokens']} | {row['Completion Tokens']} | {row['Total Tokens']} | {cost_factor}x |")
    lines.append("")
    
    lines.append("## First Attempt Analysis")
    lines.append("")
    b_first_acc = (df_first[(df_first["Mode"] == "Mode B (Production)")]["Accepted First Attempt"] == "Yes").sum()
    e_first_acc = (df_first[(df_first["Mode"] == "Mode E (Multi-Candidate Ranking)")]["Accepted First Attempt"] == "Yes").sum()
    total_first = len(df_first) // 2
    
    lines.append(f"- **Mode B (Production):** Succeeded on the first attempt for {b_first_acc}/{total_first} question variants ({b_stats['First Attempt Success Rate (%)']:.1f}%).")
    lines.append(f"- **Mode E (Multi-Candidate Ranking):** Succeeded on the first attempt for {e_first_acc}/{total_first} question variants ({e_stats['First Attempt Success Rate (%)']:.1f}%).")
    lines.append("")
    
    lines.append("## Manual Review Summary")
    lines.append("")
    winners = df_gen_comp["Winner"].value_counts()
    lines.append("Comparison of generated outputs indicates the following distribution of preferred variants:")
    for w, count in winners.items():
        pct = count / len(df_gen_comp) * 100
        lines.append(f"- **{w}:** preferred in {count}/{len(df_gen_comp)} runs ({pct:.1f}%).")
    lines.append("")
    lines.append("Detailed comparisons are recorded in `generation_comparison.csv` and `manual_review.csv`.")
    
    report_content = "\n".join(lines)
    save_text(report_content, "mode_e_benchmark_report.md")
    print("Saved mode_e_benchmark_report.md")


# ---------------------------------------------------------------------------
# Extended benchmark report for benchmark_dataset_100.json (and similar JSON
# datasets with expected_bloom / expected_difficulty / domain / topic fields)
# ---------------------------------------------------------------------------

def _confusion_matrix_text(df: pd.DataFrame, mode_name: str) -> list:
    """Return markdown lines for a Bloom-level confusion matrix for the given mode."""
    lines = []
    m = df[df["Mode"] == mode_name]
    lines.append("| Target \\ Predicted | " + " | ".join(BLOOM_LEVELS) + " |")
    lines.append("|---" * (len(BLOOM_LEVELS) + 1) + "|")
    for target in BLOOM_LEVELS:
        row = []
        for pred in BLOOM_LEVELS:
            count = ((m["Target Bloom"] == target) & (m["Predicted Bloom"] == pred)).sum()
            row.append(str(count))
        lines.append(f"| {target} | " + " | ".join(row) + " |")
    return lines


def _per_class_prf(df: pd.DataFrame, mode_name: str, levels: list, target_col: str, pred_col: str) -> list:
    """Return rows of per-class precision, recall, F1 for given levels."""
    m = df[df["Mode"] == mode_name]
    rows = []
    macro_p, macro_r, macro_f = 0.0, 0.0, 0.0
    for lvl in levels:
        tp = ((m[target_col] == lvl) & (m[pred_col] == lvl)).sum()
        fp = ((m[target_col] != lvl) & (m[pred_col] == lvl)).sum()
        fn = ((m[target_col] == lvl) & (m[pred_col] != lvl)).sum()
        p = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        r = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0.0
        rows.append({"Class": lvl, "Precision": round(p, 3), "Recall": round(r, 3), "F1": round(f1, 3)})
        macro_p += p; macro_r += r; macro_f += f1
    n = len(levels)
    rows.append({"Class": "**Macro**", "Precision": round(macro_p / n, 3),
                 "Recall": round(macro_r / n, 3), "F1": round(macro_f / n, 3)})
    return rows


def generate_benchmark_100_report(
    df_eval: pd.DataFrame,
    json_dataset: list,
    comparison_stats: list,
    failure_analysis_results: list,
) -> None:
    """Generate benchmark_results.csv and benchmark_report_100.md from a JSON dataset run."""

    DIFFICULTY_LEVELS = ["Easy", "Medium", "Hard"]
    lines = []


    # --- benchmark_results.csv ---
    # Include only the columns relevant to the extended benchmark
    csv_cols = [
        "Mode", "Source Question", "Target Bloom", "Predicted Bloom",
        "Target Difficulty", "Predicted Difficulty", "Confidence",
        "Concept Match Score", "Overall Pass", "Rejection Reason",
        "Attempts", "Generation Time", "Flan Calls", "Deberta Calls",
        "Candidates Generated", "Candidates Validated",
    ]
    available_cols = [c for c in csv_cols if c in df_eval.columns]
    save_dataframe(df_eval[available_cols], "benchmark_results.csv")
    print("Saved benchmark_results.csv")

    # --- benchmark_report_100.md ---
    lines.append("# BloomAI Arena v2.1 — Extended Benchmark Report (100 Questions)")
    lines.append("")
    lines.append(
        "This report evaluates **Mode B (Production)** and **Mode E (Multi-Candidate Ranking)** "
        "on a manually curated 100-question university examination dataset "
        "(`benchmark_dataset_100.json`) spanning 8 domains and all six Bloom levels."
    )
    lines.append("")

    # ── Overall Summary ──────────────────────────────────────────────────────
    lines.append("## 1. Overall Summary")
    lines.append("")
    lines.append("| Metric | Mode B (Production) | Mode E (Multi-Candidate) |")
    lines.append("|---|---|---|")

    summary_keys = [
        ("Overall Pass Rate (%)", "Overall Pass Rate"),
        ("First Attempt Success Rate (%)", "First Attempt Success Rate"),
        ("Bloom Accuracy (%)", "Bloom Accuracy"),
        ("Difficulty Accuracy (%)", "Difficulty Accuracy"),
        ("Concept Preservation (%)", "Concept Preservation"),
        ("Duplicate Rate (%)", "Duplicate Rate"),
        ("Average Confidence (%)", "Avg Confidence"),
        ("Average Generation Time (s)", "Avg Generation Time (s)"),
        ("Average FLAN Calls", "Avg FLAN Calls"),
        ("Average DeBERTa Calls", "Avg DeBERTa Calls"),
        ("Failure Rate (%)", "Failure Rate"),
    ]

    b_stats = next((s for s in comparison_stats if "Mode B" in s["Mode"]), {})
    e_stats = next((s for s in comparison_stats if "Mode E" in s["Mode"]), {})

    for stat_key, label in summary_keys:
        bv = b_stats.get(stat_key, "N/A")
        ev = e_stats.get(stat_key, "N/A")
        lines.append(f"| {label} | {bv} | {ev} |")
    lines.append("")

    # ── Bloom Statistics ─────────────────────────────────────────────────────
    lines.append("## 2. Bloom-Level Statistics")
    lines.append("")
    for mode_name in ["Mode B (Production)", "Mode E (Multi-Candidate Ranking)"]:
        short = "Mode B" if "Mode B" in mode_name else "Mode E"
        lines.append(f"### {short} — Per-Bloom Accuracy")
        lines.append("")
        lines.append("| Bloom Level | Questions | Passed | Accuracy |")
        lines.append("|---|---|---|---|")
        m = df_eval[df_eval["Mode"] == mode_name]
        for lvl in BLOOM_LEVELS:
            sub = m[m["Target Bloom"] == lvl]
            n = len(sub)
            passed = (sub["Overall Pass"] == "Pass").sum()
            acc = f"{passed / n * 100:.1f}%" if n > 0 else "N/A"
            lines.append(f"| {lvl} | {n} | {passed} | {acc} |")
        lines.append("")

        lines.append(f"### {short} — Per-Bloom Precision / Recall / F1")
        lines.append("")
        lines.append("| Bloom Level | Precision | Recall | F1 |")
        lines.append("|---|---|---|---|")
        for row in _per_class_prf(df_eval, mode_name, BLOOM_LEVELS, "Target Bloom", "Predicted Bloom"):
            lines.append(f"| {row['Class']} | {row['Precision']} | {row['Recall']} | {row['F1']} |")
        lines.append("")

    # ── Difficulty Statistics ─────────────────────────────────────────────────
    lines.append("## 3. Difficulty-Level Statistics")
    lines.append("")
    for mode_name in ["Mode B (Production)", "Mode E (Multi-Candidate Ranking)"]:
        short = "Mode B" if "Mode B" in mode_name else "Mode E"
        lines.append(f"### {short} — Per-Difficulty Accuracy")
        lines.append("")
        lines.append("| Difficulty | Questions | Passed | Accuracy |")
        lines.append("|---|---|---|---|")
        m = df_eval[df_eval["Mode"] == mode_name]
        for lvl in DIFFICULTY_LEVELS:
            sub = m[m["Target Difficulty"] == lvl]
            n = len(sub)
            passed = (sub["Overall Pass"] == "Pass").sum()
            acc = f"{passed / n * 100:.1f}%" if n > 0 else "N/A"
            lines.append(f"| {lvl} | {n} | {passed} | {acc} |")
        lines.append("")

        lines.append(f"### {short} — Per-Difficulty Precision / Recall / F1")
        lines.append("")
        lines.append("| Difficulty | Precision | Recall | F1 |")
        lines.append("|---|---|---|---|")
        for row in _per_class_prf(df_eval, mode_name, DIFFICULTY_LEVELS, "Target Difficulty", "Predicted Difficulty"):
            lines.append(f"| {row['Class']} | {row['Precision']} | {row['Recall']} | {row['F1']} |")
        lines.append("")

    # ── Bloom Confusion Matrices ──────────────────────────────────────────────
    lines.append("## 4. Bloom Confusion Matrices")
    lines.append("")
    for mode_name in ["Mode B (Production)", "Mode E (Multi-Candidate Ranking)"]:
        short = "Mode B" if "Mode B" in mode_name else "Mode E"
        lines.append(f"### {short}")
        lines.append("")
        lines.extend(_confusion_matrix_text(df_eval, mode_name))
        lines.append("")

    # ── Failure Analysis ──────────────────────────────────────────────────────
    lines.append("## 5. Failure Analysis")
    lines.append("")
    for mode_name in ["Mode B (Production)", "Mode E (Multi-Candidate Ranking)"]:
        short = "Mode B" if "Mode B" in mode_name else "Mode E"
        m_fails = df_eval[(df_eval["Mode"] == mode_name) & (df_eval["Overall Pass"] == "Fail")]
        lines.append(f"### {short} — {len(m_fails)} Failures")
        lines.append("")
        if len(m_fails) > 0:
            reasons = m_fails["Rejection Reason"].value_counts()
            lines.append("| Rejection Reason | Count | % |")
            lines.append("|---|---|---|")
            for reason, count in reasons.items():
                if reason and str(reason) not in ("None", "N/A", "nan"):
                    pct = count / len(m_fails) * 100
                    lines.append(f"| {reason} | {count} | {pct:.1f}% |")
        else:
            lines.append("No failures recorded.")
        lines.append("")

    # ── Duplicate Analysis ────────────────────────────────────────────────────
    lines.append("## 6. Duplicate Analysis")
    lines.append("")
    lines.append("| Mode | Duplicate Count | Duplicate Rate |")
    lines.append("|---|---|---|")
    for mode_name in ["Mode B (Production)", "Mode E (Multi-Candidate Ranking)"]:
        m = df_eval[df_eval["Mode"] == mode_name]
        dup_count = (m["Rejection Reason"] == "Duplicate").sum()
        dup_rate = dup_count / len(m) * 100 if len(m) > 0 else 0.0
        lines.append(f"| {mode_name} | {dup_count} | {dup_rate:.1f}% |")
    lines.append("")

    # ── Timing Analysis ───────────────────────────────────────────────────────
    lines.append("## 7. Generation Timing Analysis")
    lines.append("")
    lines.append("| Mode | Avg Time (s) | Avg FLAN Calls | Avg DeBERTa Calls | Avg Candidates Generated |")
    lines.append("|---|---|---|---|---|")
    for mode_name in ["Mode B (Production)", "Mode E (Multi-Candidate Ranking)"]:
        m = df_eval[df_eval["Mode"] == mode_name]
        avg_t = m["Generation Time"].mean() if len(m) > 0 else 0.0
        avg_f = m["Flan Calls"].mean() if "Flan Calls" in m.columns else 0.0
        avg_d = m["Deberta Calls"].mean() if "Deberta Calls" in m.columns else 0.0
        avg_c = m["Candidates Generated"].mean() if "Candidates Generated" in m.columns else 0.0
        lines.append(f"| {mode_name} | {avg_t:.2f} | {avg_f:.2f} | {avg_d:.2f} | {avg_c:.2f} |")
    lines.append("")

    # ── Recommendation ────────────────────────────────────────────────────────
    lines.append("## 8. Final Recommendation")
    lines.append("")
    b_pass = b_stats.get("Overall Pass Rate (%)", 0)
    e_pass = e_stats.get("Overall Pass Rate (%)", 0)
    b_time = b_stats.get("Average Generation Time (s)", 9999)
    e_time = e_stats.get("Average Generation Time (s)", 9999)
    b_bloom = b_stats.get("Bloom Accuracy (%)", 0)
    e_bloom = e_stats.get("Bloom Accuracy (%)", 0)

    latency_improved = (e_time <= b_time * 0.85) if b_time > 0 else False
    quality_maintained = (e_pass >= b_pass and e_bloom >= b_bloom)

    if quality_maintained and latency_improved:
        lines.append("> [!IMPORTANT]")
        lines.append("> **PROMOTE TO PRODUCTION.** Mode E maintains quality parity with Mode B ")
        lines.append("> while achieving significant latency reduction on the extended benchmark.")
    elif quality_maintained:
        lines.append("> [!NOTE]")
        lines.append("> **CONDITIONALLY ACCEPTABLE.** Mode E matches Mode B quality but does not ")
        lines.append("> achieve the 15% latency improvement target on this larger dataset.")
    else:
        lines.append("> [!WARNING]")
        lines.append("> **DO NOT PROMOTE.** Mode E failed to match Mode B quality on the extended benchmark.")
    lines.append("")

    report_text = "\n".join(lines)
    save_text(report_text, "benchmark_report_100.md")
    print("Saved benchmark_report_100.md")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="BloomAI Arena v2.1 Evaluation Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python evaluate_pipeline.py\n"
            "      Runs the default benchmark (benchmark_questions.csv).\n"
            "  python evaluate_pipeline.py --dataset benchmark_dataset_100.json\n"
            "      Runs the extended 100-question benchmark.\n"
        ),
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default=None,
        help="Path to a JSON benchmark dataset file (relative to the project directory). "
             "If omitted, the default benchmark_questions.csv is used.",
    )
    parser.add_argument(
        "--model-version",
        type=str,
        choices=["v9", "new"],
        default="v9",
        help="Select the model version to evaluate ('v9' or 'new'). Default: 'v9'."
    )
    args = parser.parse_args()
    run_benchmark(dataset_path=args.dataset, model_version=args.model_version)
