import os
import re

md_path = r"c:\Tharun\BloomAI_Arena_v2_1\report\BloomEngine_MCA_Major_Project_Report.md"

with open(md_path, "r", encoding="utf-8") as f:
    content = f.read()

# New Chapter 5 & 6 text matching exact empirical dataset analysis
new_ch5_ch6 = """# CHAPTER 5: DATA COLLECTION AND PREPARATION

## 5.1 Data Sources

The **BloomEngine** machine learning pipeline is supported by a comprehensive multi-dataset repository comprising 52,570 total records across eight dedicated file assets:

1. **FLAN-T5 SFT Instruction Fine-Tuning Corpus (`Datasets/combined_cleaned.json`)**: 21,004 supervised fine-tuning triplets (`instruction`, `input`, `output`) used exclusively for training the sequence-to-sequence question transformation generator.
2. **DeBERTa-v3 Cognitive Classifier Dataset (`final_dataset_v2.xlsx`)**: 31,310 domain-annotated assessment questions (`Question`, `Bloom_Level`, `Cognitive_Level_Number`, `Difficulty`) spanning core Computer Science domains (DBMS, Computer Networks, Operating Systems, Machine Learning, Artificial Intelligence).
3. **Comprehensive Evaluation Benchmark (`benchmark_dataset.json`)**: 300 curated questions (`question`, `expected_bloom`) for cross-validation.
4. **Standardized 100-Item Benchmark Suite (`benchmark_dataset_100.json`)**: 100 benchmark items (`question`, `expected_bloom`, `expected_difficulty`, `domain`, `topic`) used for automated evaluation and Playwright testing.
5. **Human Expert Validation Dataset (`manual_review.csv`)**: 100 review items containing qualitative reviewer scores, generation timing, and failure annotations.
6. **Candidate Ranking Diagnostic Log (`candidate_ranking_log.json`)**: 651 candidate generation records tracking individual 7-stage scores, confidence metrics, and rank selection logs.
7. **FLAN-T5 Test Predictions Log (`flan_t5_model/model_predictions.csv`)**: 100 evaluation outputs comparing ground-truth targets with model predictions.
8. **Smoke-Testing Dataset (`benchmark_questions.csv`)**: 5 lightweight test cases for REST API route verification.

*Table 5.1: Empirical Dataset Summary Across Repository Files.*

| Dataset File Name | Format | Record Count | File Size | Primary Fields / Columns | Primary Application Task |
| :--- | :---: | :---: | :---: | :--- | :--- |
| **`combined_cleaned.json`** | JSON | **21,004** | 11.80 MB | `instruction`, `input`, `output` | FLAN-T5 Seq2Seq SFT Generation |
| **`final_dataset_v2.xlsx`** | XLSX | **31,310** | 1.40 MB | `Question`, `Bloom_Level`, `Cognitive_Level_Number`, `Difficulty` | DeBERTa-v3 6-Class Classification |
| **`benchmark_dataset.json`** | JSON | **300** | 0.043 MB | `question`, `expected_bloom` | Comprehensive Pipeline Validation |
| **`benchmark_dataset_100.json`**| JSON | **100** | 0.027 MB | `question`, `expected_bloom`, `expected_difficulty`, `domain`, `topic` | Benchmark Alignment & Testing |
| **`manual_review.csv`** | CSV | **100** | 0.030 MB | `Original Question`, `Generated Question`, `Source Bloom`, `Target Bloom`, `Confidence` | Expert Quality & Error Audit |
| **`candidate_ranking_log.json`**| JSON | **651** | 0.315 MB | `Candidate ID`, `Question`, `Bloom Prediction`, `Validation Status`, `Rank Score` | Runtime Candidate Scoring Audit |
| **`model_predictions.csv`** | CSV | **100** | 0.037 MB | `Input`, `Expected`, `Predicted` | Test Prediction & BLEU Evaluation |
| **`benchmark_questions.csv`** | CSV | **5** | 436 Bytes | `Question` | REST Endpoint Smoke Testing |
| **Total Corpus** | — | **53,570** | **~13.63 MB** | — | **Full Machine Learning Lifecycle** |

---

## 5.2 Data Profiling

Data profiling across the 31,310-record classifier dataset (`final_dataset_v2.xlsx`) and 21,004-record seq2seq dataset (`combined_cleaned.json`) demonstrates high structural integrity:
- **Missing Value Rate**: **0.00% null values** across all mandatory fields (`Question`, `Bloom_Level`, `Cognitive_Level_Number`, `Difficulty`, `instruction`, `input`, `output`).
- **Exact Duplicate Rate**: **0.00% duplicates** in `final_dataset_v2.xlsx` (31,310 unique questions).
- **Data Leakage Control**: String matching between the training set and `benchmark_dataset_100.json` confirmed **0.00% overlap**, preventing test evaluation bias.

---

## 5.3 Data Cleaning and Preprocessing

Preprocessing involves a deterministic four-stage pipeline:
1. **Lowercase & ASCII Normalization**: Stripping non-standard unicode characters and mapping all strings to standard ASCII text.
2. **CS Abbreviation Expansion**: Expanding technical acronyms via `ABBREVIATION_MAP` (e.g., "sql" $\rightarrow$ "structured query language", "tcp" $\rightarrow$ "transmission control protocol").
3. **Whitespace & Punctuation Standardization**: Removing extra spaces, normalizing hyphens, and standardizing trailing question marks.
4. **Instruction Format Assembly**: Converting raw question pairs into canonical SFT triplets (`instruction`, `input`, `output`).

---

# CHAPTER 6: EXPLORATORY DATA ANALYSIS

## 6.1 Data Visualization Techniques

Exploratory Data Analysis (EDA) was performed across sentence length, vocabulary richness, difficulty balance, and Bloom taxonomy class distributions.

## 6.2 Univariate and Bivariate Analysis

### 6.2.1 Sentence Length & Vocabulary Diversity
- **Average Question Length**: $14.25 \pm 7.30$ words per question (Min: 3 words, Max: 60 words).
- **Average Character Length**: 105.07 characters per item.
- **Total Token Volume**: 453,058 tokens in the classification corpus.
- **Unique Vocabulary**: 12,284 unique words.
- **Vocabulary Diversity Ratio (Type-Token Ratio)**: **0.0271** (reflecting dense domain-specific CS terminology repetition).

### 6.2.2 Class & Difficulty Balance Analysis

*Table 6.1: Difficulty Tier Distribution (`final_dataset_v2.xlsx`).*

| Difficulty Tier | Record Count | Percentage (%) | Cognitive Level Association |
| :--- | :---: | :---: | :--- |
| **Hard** | 12,199 | 38.96% | *Analyze*, *Evaluate*, *Create* |
| **Easy** | 9,628 | 30.75% | *Remember*, *Understand* |
| **Medium** | 9,483 | 30.29% | *Apply*, *Analyze* |
| **Total** | **31,310** | **100.00%** | **6 Bloom Cognitive Tiers** |
"""

# Replace Chapter 5 and Chapter 6 in content
start_marker = "# CHAPTER 5: DATA COLLECTION AND PREPARATION"
end_marker = "# CHAPTER 7: METHODOLOGY"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx != -1 and end_idx != -1:
    updated_content = content[:start_idx] + new_ch5_ch6 + "\n---\n\n" + content[end_idx:]
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(updated_content)
    print("Successfully updated Chapter 5 & 6 in master markdown report!")
else:
    print("Markers not found!")
