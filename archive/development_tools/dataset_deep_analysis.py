import os
import json
import pandas as pd
import numpy as np
from collections import Counter, defaultdict
import re

def analyze_datasets():
    print("=" * 80)
    print("   BLOOMENGINE DEEP DATASET INSPECTION & COMPREHENSIVE ANALYSIS REPORT")
    print("=" * 80)

    # 1. Datasets to inspect
    files_to_inspect = {
        "combined_cleaned.json": r".\Datasets\combined_cleaned.json",
        "final_dataset_v2.xlsx": r".\final_dataset_v2.xlsx",
        "benchmark_dataset.json": r".\benchmark_dataset.json",
        "benchmark_dataset_100.json": r".\benchmark_dataset_100.json",
        "manual_review.csv": r".\manual_review.csv",
        "candidate_ranking_log.json": r".\candidate_ranking_log.json",
        "model_predictions.csv": r".\flan_t5_model\model_predictions.csv",
        "benchmark_questions.csv": r".\benchmark_questions.csv"
    }

    all_stats = {}

    for name, path in files_to_inspect.items():
        if not os.path.exists(path):
            print(f"[MISSING] {name} at {path}")
            continue

        print(f"\n--- Analyzing: {name} (Path: {path}) ---")
        file_size = os.path.getsize(path)
        print(f"File Size: {file_size / (1024*1024):.3f} MB ({file_size:,} bytes)")

        if name.endswith(".json"):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                # Check dict keys
                print(f"Top-level Dict Keys: {list(data.keys())[:10]}")
                if "results" in data:
                    df = pd.DataFrame(data["results"])
                elif "questions" in data:
                    df = pd.DataFrame(data["questions"])
                else:
                    # Flatten dict or list of items
                    first_key = list(data.keys())[0]
                    if isinstance(data[first_key], list):
                        df = pd.DataFrame(data[first_key])
                    else:
                        df = pd.DataFrame([data])
        elif name.endswith(".xlsx"):
            df = pd.read_excel(path)
        elif name.endswith(".csv"):
            df = pd.read_csv(path)
        
        num_rows = len(df)
        cols = list(df.columns)
        print(f"Record Count: {num_rows:,} rows | Columns ({len(cols)}): {cols}")

        # Check missing values
        null_counts = df.isnull().sum().to_dict()
        print(f"Missing Values per Column: {null_counts}")

        # Check duplicates
        # Find primary text column
        text_col = None
        for candidate in ["question", "Question", "input_text", "prompt", "Source Question", "source_question"]:
            if candidate in df.columns:
                text_col = candidate
                break
        
        if text_col:
            dup_count = df.duplicated(subset=[text_col]).sum()
            print(f"Primary Text Column identified: '{text_col}'")
            print(f"Duplicate Text Entries: {dup_count} ({(dup_count/num_rows)*100:.2f}%)")

            # Word count analysis
            text_series = df[text_col].dropna().astype(str)
            word_counts = text_series.apply(lambda x: len(x.split()))
            char_counts = text_series.apply(len)

            vocab = Counter()
            for t in text_series:
                tokens = re.findall(r'\w+', t.lower())
                vocab.update(tokens)

            print(f"Average Word Count: {word_counts.mean():.2f} ± {word_counts.std():.2f} (Min: {word_counts.min()}, Max: {word_counts.max()})")
            print(f"Average Character Length: {char_counts.mean():.2f}")
            print(f"Unique Vocabulary Size: {len(vocab):,} unique tokens | Total Tokens: {sum(vocab.values()):,}")
            print(f"Vocabulary Diversity Ratio (Type-Token Ratio): {len(vocab)/max(1, sum(vocab.values())):.4f}")

        # Check Bloom level / difficulty columns
        bloom_col = None
        for candidate in ["bloom_level", "Bloom Level", "bloom", "target_bloom", "Predicted Bloom", "predicted_bloom", "Bloom"]:
            if candidate in df.columns:
                bloom_col = candidate
                break
        
        if bloom_col:
            print(f"Bloom Level Column: '{bloom_col}'")
            bloom_dist = df[bloom_col].value_counts().to_dict()
            print(f"Bloom Class Distribution: {bloom_dist}")

        diff_col = None
        for candidate in ["difficulty", "Difficulty", "target_difficulty", "predicted_difficulty"]:
            if candidate in df.columns:
                diff_col = candidate
                break
        
        if diff_col:
            print(f"Difficulty Column: '{diff_col}'")
            diff_dist = df[diff_col].value_counts().to_dict()
            print(f"Difficulty Distribution: {diff_dist}")

        all_stats[name] = {
            "num_rows": num_rows,
            "columns": cols,
            "null_counts": null_counts,
            "text_col": text_col,
            "bloom_col": bloom_col,
            "file_size": file_size
        }

    # Cross-dataset correlation & Data Leakage Check
    print("\n" + "=" * 80)
    print("   CROSS-DATASET LEAKAGE & OVERLAP CHECK")
    print("=" * 80)

    if os.path.exists(files_to_inspect["combined_cleaned.json"]) and os.path.exists(files_to_inspect["benchmark_dataset_100.json"]):
        with open(files_to_inspect["combined_cleaned.json"], "r", encoding="utf-8") as f:
            comb_data = json.load(f)
        with open(files_to_inspect["benchmark_dataset_100.json"], "r", encoding="utf-8") as f:
            bench_data = json.load(f)

        comb_texts = set()
        for item in comb_data:
            t = item.get("question") or item.get("input_text") or item.get("prompt") or ""
            if t:
                comb_texts.add(t.strip().lower())

        bench_texts = set()
        for item in bench_data:
            t = item.get("question") or item.get("input_text") or item.get("source_question") or ""
            if t:
                bench_texts.add(t.strip().lower())

        overlap = comb_texts.intersection(bench_texts)
        print(f"Total Unique Training Prompts (combined_cleaned.json): {len(comb_texts):,}")
        print(f"Total Unique Benchmark Questions (benchmark_dataset_100.json): {len(bench_texts):,}")
        print(f"Exact Overlap / Data Leakage Count: {len(overlap)} questions ({(len(overlap)/max(1, len(bench_texts)))*100:.2f}%)")

if __name__ == "__main__":
    analyze_datasets()
