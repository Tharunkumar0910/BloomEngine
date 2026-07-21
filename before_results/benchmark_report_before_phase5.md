# BloomAI Arena v2.1 Pipeline Alignment Report

## Executive Summary
This report summarizes the benchmark evaluation of the aligned FLAN-T5 inference pipeline on **100** questions from `benchmark_dataset_100.json`.
The inference pipeline has been aligned to match the training prompt distribution exactly on attempt 1, with Mode E retry logic enabled on subsequent attempts.

### Key Quality & Performance Metrics
- **Validation Pass Rate**: 87.00%
- **Bloom Exact Match Rate**: 98.00%
- **Average Bloom Confidence**: 99.58%
- **Concept Validation Success**: 100.00%
- **Duplicate Rejection Rate**: 9.72%
- **Average Generation Time**: 6.66 seconds
- **Average Retries per Question**: 0.68

---

## Comparison with Baseline (Before Refactoring)

| Metric | Baseline | Current (After Refactoring) | Delta |
| :--- | :---: | :---: | :---: |
| **Validation Pass Rate** | 90.00% | 87.00% | -3.00% |
| **Bloom Exact Match Rate** | 99.00% | 98.00% | -1.00% |
| **Average Bloom Confidence** | 99.98% | 99.58% | -0.41% |
| **Concept Validation Success** | 92.00% | 100.00% | +8.00% |
| **Duplicate Rejection Rate** | 5.21% | 9.72% | +4.51% |
| **Average Generation Time** | 2.97s | 6.66s | +3.69s |
| **Average Retries** | 0.19 | 0.68 | +0.49 |
| **BLEU Score** | 0.3058 | 0.3482 | +0.0424 |
| **ROUGE-L Score** | 0.5293 | 0.5653 | +0.0360 |

---

## NLP Semantic Overlap Metrics (Compared to Source Question)
- **BLEU Score**: 0.3482
- **ROUGE-1**: 0.6131
- **ROUGE-2**: 0.4388
- **ROUGE-L**: 0.5653

---

## Top Semantic Drift Causes
| Rank | Category | Count | Percentage |
| :---: | :--- | :---: | :---: |
| 1 | Concept Removal | 295 | 73.57% |
| 2 | Intent Change | 87 | 21.70% |
| 3 | Protocol Change | 15 | 3.74% |
| 4 | Numeric Change | 3 | 0.75% |
| 5 | Algorithm Change | 1 | 0.25% |
| 6 | Concept Addition | 0 | 0.00% |
| 7 | Terminology Change | 0 | 0.00% |
| 8 | Entity Change | 0 | 0.00% |
| 9 | Domain Vocabulary Change | 0 | 0.00% |
| 10 | Topic Vocabulary Change | 0 | 0.00% |
| 11 | Equivalent Technical Concepts | 0 | 0.00% |

---

## Performance by Bloom Level
| Bloom Level | Count | Pass Rate (%) | Exact Match (%) | Avg Conf (%) | Avg Retries | Avg Time (s) | BLEU | ROUGE-L |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Remember | 17 | 88.2% | 100.0% | 99.7% | 0.5 | 3.7s | 0.353 | 0.586 |
| Understand | 17 | 88.2% | 94.1% | 99.7% | 0.9 | 6.2s | 0.258 | 0.505 |
| Apply | 16 | 100.0% | 100.0% | 100.0% | 0.2 | 7.0s | 0.345 | 0.543 |
| Analyze | 16 | 62.5% | 100.0% | 100.0% | 1.5 | 9.9s | 0.288 | 0.511 |
| Evaluate | 17 | 88.2% | 94.1% | 98.2% | 0.4 | 5.6s | 0.364 | 0.591 |
| Create | 17 | 94.1% | 100.0% | 100.0% | 0.5 | 7.8s | 0.476 | 0.652 |


---

## Retry Analysis
### Retry Distribution
| Retries | Question Count |
|---|---|
| 0 | 70 |
| 1 | 8 |
| 2 | 6 |
| 3 | 16 |

### Attempt Success Breakdown
| Attempt | Passed Candidates |
|---|---|
| Attempt 1 Success | 143 |
| Attempt 2 Success | 12 |
| Attempt 3 Success | 7 |
| Attempt 4Plus Success | 3 |

### Failed Candidates Rejection Reasons
| Reason | Count |
|---|---|
| Semantic Drift | 225 |
| Classification Mismatch | 85 |
| Duplicate | 55 |
| Domain Mismatch | 17 |
| Domain Drift | 15 |
| Topic Mismatch | 4 |

---

## Average Stage Scores (All Candidates)
| Stage | Max Points | Average Score |
|---|---|---|
| **Bloom** | 35.0 | 29.6486 |
| **Domain** | 20.0 | 14.8057 |
| **Topic** | 15.0 | 9.9128 |
| **Concept** | 10.0 | 4.9452 |
| **Entity** | 10.0 | 6.5925 |
| **Number** | 5.0 | 4.9382 |
| **Grammar** | 3.0 | 2.8813 |
| **Duplicate** | 2.0 | 1.7491 |
| **Total** | 100.0 | 74.5616 |

---

## Validation Failure Distribution
| Rejection Reason | Count |
|---|---|
| Semantic Drift | 225 |
| Classification Mismatch | 85 |
| Duplicate | 55 |
| Domain Mismatch | 17 |
| Domain Drift | 15 |
| Topic Mismatch | 4 |

---

## Conclusion
The aligned FLAN-T5 generation pipeline satisfies both natural question structure requirements and cognitive rigor as enforced by DeBERTa classification, concept matching, and semantic duplicate validation.
