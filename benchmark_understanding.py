"""
benchmark_understanding.py
==========================
Evaluates the hierarchical QuestionUnderstandingEngine on benchmark datasets.
Measures:
- Domain accuracy & Top-3 Domain accuracy
- Topic accuracy & Top-3 Topic accuracy
- Average confidence (Domain & Topic)
- Latency (first run, second run cached)
- Cache Hit Rate
"""

import json
import os
import sys
import time
import json
import os
import sys
import time

# Robust tabulate fallback for environments without it
try:
    from tabulate import tabulate
except ImportError:
    def tabulate(rows, headers=None):
        if headers == "firstrow":
            headers = rows[0]
            rows = rows[1:]
        out = []
        if headers:
            out.append(" | ".join(str(h) for h in headers))
            out.append("-+-".join("-" * len(str(h)) for h in headers))
        for row in rows:
            out.append(" | ".join(str(r) for r in row))
        return "\n".join(out)

# Ensure we can import from the current directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from question_understanding import QuestionUnderstandingEngine

def run_benchmark(dataset_name: str, dataset_path: str):
    print(f"\n==============================================")
    print(f"Evaluating {dataset_name}")
    print(f"Source: {dataset_path}")
    print(f"==============================================")

    if not os.path.exists(dataset_path):
        print(f"[ERROR] Dataset file not found at: {dataset_path}")
        return

    with open(dataset_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    print(f"Loaded {len(records)} test records.")

    # Reset cache before starting
    from question_understanding import profile_cache
    profile_cache.clear()

    # Pass 1: Cold start (un-cached)
    start_time = time.time()
    results = []
    for rec in records:
        q = rec["question"]
        t_start = time.time()
        profile = QuestionUnderstandingEngine.build_profile(q)
        latency = (time.time() - t_start) * 1000.0  # ms
        results.append((rec, profile, latency))
    first_pass_duration = (time.time() - start_time) * 1000.0

    # Pass 2: Hot start (cached)
    start_time_hot = time.time()
    for rec in records:
        _ = QuestionUnderstandingEngine.build_profile(rec["question"])
    second_pass_duration = (time.time() - start_time_hot) * 1000.0

    # Compile metrics
    domain_correct = 0
    domain_in_top3 = 0
    topic_correct = 0
    topic_in_top3 = 0
    
    total_domain_conf = 0.0
    total_topic_conf = 0.0
    total_latency = 0.0
    
    mismatches = []
    total = len(records)
    has_labels = total > 0 and "domain" in records[0]

    for rec, profile, latency in results:
        expected_domain = rec.get("domain")
        expected_topic = rec.get("topic")
        
        pred_domain = profile.domain
        pred_topic = profile.topic
        
        if has_labels and expected_domain and expected_topic:
            # Exact checks
            is_domain_correct = pred_domain.lower() == expected_domain.lower()
            is_topic_correct = pred_topic.lower() == expected_topic.lower()
            
            if is_domain_correct:
                domain_correct += 1
            else:
                mismatches.append({
                    "type": "Domain",
                    "question": rec["question"],
                    "expected": expected_domain,
                    "predicted": pred_domain,
                    "confidence": profile.domain_confidence
                })
                
            if is_topic_correct:
                topic_correct += 1
            else:
                mismatches.append({
                    "type": "Topic",
                    "question": rec["question"],
                    "expected": expected_topic,
                    "predicted": pred_topic,
                    "confidence": profile.topic_confidence
                })

            # Top-3 checks
            top3_domains = [d.lower() for d in list(profile.candidate_domains.keys())[:3]]
            if expected_domain.lower() in top3_domains:
                domain_in_top3 += 1
                
            top3_topics = [t.lower() for t in list(profile.candidate_topics.keys())[:3]]
            if expected_topic.lower() in top3_topics:
                topic_in_top3 += 1
            
        total_domain_conf += profile.domain_confidence
        total_topic_conf += profile.topic_confidence
        total_latency += latency

    avg_latency = total_latency / total
    avg_domain_conf = total_domain_conf / total
    avg_topic_conf = total_topic_conf / total
    
    cache_stats = QuestionUnderstandingEngine.cache_stats()

    if has_labels:
        domain_acc = (domain_correct / total) * 100.0
        domain_top3_acc = (domain_in_top3 / total) * 100.0
        topic_acc = (topic_correct / total) * 100.0
        topic_top3_acc = (topic_in_top3 / total) * 100.0

        print(f"\n--- Accuracy Results ---")
        metrics_table = [
            ["Metric", "Value"],
            ["Domain Accuracy", f"{domain_acc:.2f}% ({domain_correct}/{total})"],
            ["Top-3 Domain Accuracy", f"{domain_top3_acc:.2f}% ({domain_in_top3}/{total})"],
            ["Topic Accuracy", f"{topic_acc:.2f}% ({topic_correct}/{total})"],
            ["Top-3 Topic Accuracy", f"{topic_top3_acc:.2f}% ({topic_in_top3}/{total})"],
        ]
        print(tabulate(metrics_table, headers="firstrow"))
    else:
        print(f"\n--- Accuracy Results ---")
        print("No ground truth labels in dataset. Skipping accuracy calculations.")

    print(f"\n--- Performance & Confidence ---")
    perf_table = [
        ["Metric", "Value"],
        ["Average Domain Confidence", f"{avg_domain_conf:.4f}"],
        ["Average Topic Confidence", f"{avg_topic_conf:.4f}"],
        ["Avg Latency (Cold)", f"{avg_latency:.2f} ms"],
        ["First Pass Total Duration", f"{first_pass_duration:.2f} ms"],
        ["Second Pass Total (Cached)", f"{second_pass_duration:.2f} ms"],
        ["Cache Hit Rate (after Pass 2)", f"{cache_stats['hit_rate']*100:.2f}%"],
    ]
    print(tabulate(perf_table, headers="firstrow"))

    if has_labels and mismatches:
        print(f"\n--- Top 5 Mismatches ---")
        for i, m in enumerate(mismatches[:5]):
            print(f"{i+1}. [{m['type']}] '{m['question']}'")
            print(f"   Expected : {m['expected']}")
            print(f"   Predicted: {m['predicted']} (Conf: {m['confidence']:.2f})")

if __name__ == "__main__":
    run_benchmark("100-Question Subset", "benchmark_dataset_100.json")
    run_benchmark("Full Dataset", "benchmark_dataset.json")
