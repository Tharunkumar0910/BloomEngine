# BloomAI Arena v2.1 Pipeline Alignment Report

## Executive Summary
This report summarizes the benchmark evaluation of the aligned FLAN-T5 inference pipeline on **100** questions from `benchmark_dataset_100.json`.
The inference pipeline has been aligned to match the training prompt distribution exactly on attempt 1, with Mode E retry logic enabled on subsequent attempts.

### Key Quality & Performance Metrics
- **Validation Pass Rate**: 85.00%
- **Bloom Exact Match Rate**: 100.00%
- **Average Bloom Confidence**: 99.40%
- **Concept Validation Success**: 100.00%
- **Duplicate Rejection Rate**: 11.63%
- **Average Generation Time**: 6.47 seconds
- **Average Retries per Question**: 0.75

---

## Comparison with Baseline (Before Refactoring)

| Metric | Baseline | Current (After Refactoring) | Delta |
| :--- | :---: | :---: | :---: |
| **Validation Pass Rate** | 90.00% | 85.00% | -5.00% |
| **Bloom Exact Match Rate** | 99.00% | 100.00% | +1.00% |
| **Average Bloom Confidence** | 99.98% | 99.40% | -0.58% |
| **Concept Validation Success** | 92.00% | 100.00% | +8.00% |
| **Duplicate Rejection Rate** | 5.21% | 11.63% | +6.42% |
| **Average Generation Time** | 2.97s | 6.47s | +3.50s |
| **Average Retries** | 0.19 | 0.75 | +0.56 |
| **BLEU Score** | 0.3058 | 0.3285 | +0.0227 |
| **ROUGE-L Score** | 0.5293 | 0.5604 | +0.0311 |

---

## NLP Semantic Overlap Metrics (Compared to Source Question)
- **BLEU Score**: 0.3285
- **ROUGE-1**: 0.6132
- **ROUGE-2**: 0.4249
- **ROUGE-L**: 0.5604

---

## Top Semantic Drift Causes
| Rank | Category | Count | Percentage |
| :---: | :--- | :---: | :---: |
| 1 | Concept Removal | 320 | 74.25% |
| 2 | Intent Change | 86 | 19.95% |
| 3 | Protocol Change | 14 | 3.25% |
| 4 | Terminology Change | 5 | 1.16% |
| 5 | Algorithm Change | 3 | 0.70% |
| 6 | Numeric Change | 2 | 0.46% |
| 7 | Entity Change | 1 | 0.23% |
| 8 | Concept Addition | 0 | 0.00% |
| 9 | Domain Vocabulary Change | 0 | 0.00% |
| 10 | Topic Vocabulary Change | 0 | 0.00% |
| 11 | Equivalent Technical Concepts | 0 | 0.00% |

---

## Performance by Bloom Level
| Bloom Level | Count | Pass Rate (%) | Exact Match (%) | Avg Conf (%) | Avg Retries | Avg Time (s) | BLEU | ROUGE-L |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Remember | 17 | 94.1% | 100.0% | 97.8% | 0.5 | 3.5s | 0.410 | 0.632 |
| Understand | 17 | 82.4% | 100.0% | 99.3% | 1.2 | 5.7s | 0.276 | 0.526 |
| Apply | 16 | 93.8% | 100.0% | 100.0% | 0.2 | 4.4s | 0.333 | 0.539 |
| Analyze | 16 | 62.5% | 100.0% | 100.0% | 1.2 | 8.8s | 0.250 | 0.480 |
| Evaluate | 17 | 88.2% | 100.0% | 99.5% | 0.6 | 6.8s | 0.347 | 0.605 |
| Create | 17 | 88.2% | 100.0% | 100.0% | 0.8 | 9.7s | 0.351 | 0.574 |


---

## Retry Analysis
### Retry Distribution
| Retries | Question Count |
|---|---|
| 0 | 69 |
| 1 | 8 |
| 2 | 2 |
| 3 | 21 |

### Attempt Success Breakdown
| Attempt | Passed Candidates |
|---|---|
| Attempt 1 Success | 150 |
| Attempt 2 Success | 11 |
| Attempt 3 Success | 2 |
| Attempt 4Plus Success | 8 |

### Failed Candidates Rejection Reasons
| Reason | Count |
|---|---|
| Semantic Drift | 241 |
| Classification Mismatch | 85 |
| Duplicate | 70 |
| Domain Mismatch | 19 |
| Domain Drift | 15 |
| Entity Mismatch | 1 |

---

## Remaining Weak Terms Summary
- **Remaining Weak Terms in Final Outputs**: 0

---

## Average Stage Scores (All Candidates)
| Stage | Max Points | Average Score |
|---|---|---|
| **Bloom** | 35.0 | 30.0016 |
| **Domain** | 20.0 | 15.0831 |
| **Topic** | 15.0 | 10.5598 |
| **Concept** | 10.0 | 5.1545 |
| **Entity** | 10.0 | 6.8389 |
| **Number** | 5.0 | 4.9585 |
| **Grammar** | 3.0 | 2.9243 |
| **Duplicate** | 2.0 | 1.7143 |
| **Total** | 100.0 | 76.0029 |

---

## Validation Failure Distribution
| Rejection Reason | Count |
|---|---|
| Semantic Drift | 241 |
| Classification Mismatch | 85 |
| Duplicate | 70 |
| Domain Mismatch | 19 |
| Domain Drift | 15 |
| Entity Mismatch | 1 |

---

## Conclusion
The aligned FLAN-T5 generation pipeline satisfies both natural question structure requirements and cognitive rigor as enforced by DeBERTa classification, concept matching, and semantic duplicate validation.
