# BloomAI Arena v2.1 Pipeline Alignment Report

## Executive Summary
This report summarizes the benchmark evaluation of the aligned FLAN-T5 inference pipeline on **100** questions from `benchmark_dataset_100.json`.
The inference pipeline has been aligned to match the training prompt distribution exactly on attempt 1, with Mode E retry logic enabled on subsequent attempts.

### Key Quality & Performance Metrics
- **Validation Pass Rate**: 87.00%
- **Bloom Exact Match Rate**: 100.00%
- **Average Bloom Confidence**: 99.69%
- **Concept Validation Success**: 100.00%
- **Duplicate Rejection Rate**: 8.04%
- **Average Generation Time**: 5.02 seconds
- **Average Retries per Question**: 0.63

---

## Comparison with Baseline (Before Refactoring)

| Metric | Baseline | Current (After Refactoring) | Delta |
| :--- | :---: | :---: | :---: |
| **Validation Pass Rate** | 90.00% | 87.00% | -3.00% |
| **Bloom Exact Match Rate** | 99.00% | 100.00% | +1.00% |
| **Average Bloom Confidence** | 99.98% | 99.69% | -0.29% |
| **Concept Validation Success** | 92.00% | 100.00% | +8.00% |
| **Duplicate Rejection Rate** | 5.21% | 8.04% | +2.83% |
| **Average Generation Time** | 2.97s | 5.02s | +2.05s |
| **Average Retries** | 0.19 | 0.63 | +0.44 |
| **BLEU Score** | 0.3058 | 0.3760 | +0.0702 |
| **ROUGE-L Score** | 0.5293 | 0.5961 | +0.0668 |

---

## NLP Semantic Overlap Metrics (Compared to Source Question)
- **BLEU Score**: 0.3760
- **ROUGE-1**: 0.6463
- **ROUGE-2**: 0.4647
- **ROUGE-L**: 0.5961

---

## Performance by Bloom Level
| Bloom Level | Count | Pass Rate (%) | Exact Match (%) | Avg Conf (%) | Avg Retries | Avg Time (s) | BLEU | ROUGE-L |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Remember | 17 | 88.2% | 100.0% | 100.0% | 0.5 | 3.1s | 0.363 | 0.605 |
| Understand | 17 | 94.1% | 100.0% | 99.9% | 0.8 | 4.6s | 0.384 | 0.600 |
| Apply | 16 | 81.2% | 100.0% | 99.6% | 0.8 | 5.3s | 0.375 | 0.536 |
| Analyze | 16 | 81.2% | 100.0% | 100.0% | 0.8 | 6.0s | 0.357 | 0.540 |
| Evaluate | 17 | 76.5% | 100.0% | 98.7% | 0.8 | 6.4s | 0.292 | 0.575 |
| Create | 17 | 100.0% | 100.0% | 100.0% | 0.1 | 4.8s | 0.483 | 0.714 |


---

## Retry Analysis
### Retry Distribution
| Retries | Question Count |
|---|---|
| 0 | 71 |
| 1 | 11 |
| 2 | 2 |
| 3 | 16 |

### Attempt Success Breakdown
| Attempt | Passed Candidates |
|---|---|
| Attempt 1 Success | 147 |
| Attempt 2 Success | 16 |
| Attempt 3 Success | 2 |
| Attempt 4Plus Success | 3 |

### Failed Candidates Rejection Reasons
| Reason | Count |
|---|---|
| Semantic Drift | 219 |
| Classification Mismatch | 77 |
| Duplicate | 44 |
| Domain Mismatch | 35 |
| Topic Mismatch | 4 |

---

## Average Stage Scores (All Candidates)
| Stage | Max Points | Average Score |
|---|---|---|
| **Bloom** | 35.0 | 30.0289 |
| **Domain** | 20.0 | 15.5393 |
| **Topic** | 15.0 | 11.4808 |
| **Concept** | 10.0 | 6.0420 |
| **Entity** | 10.0 | 6.7313 |
| **Number** | 5.0 | 4.9726 |
| **Grammar** | 3.0 | 2.9210 |
| **Duplicate** | 2.0 | 1.7587 |
| **Total** | 100.0 | 78.1774 |

---

## Validation Failure Distribution
| Rejection Reason | Count |
|---|---|
| Semantic Drift | 219 |
| Classification Mismatch | 77 |
| Duplicate | 44 |
| Domain Mismatch | 35 |
| Topic Mismatch | 4 |

---

## Conclusion
The aligned FLAN-T5 generation pipeline satisfies both natural question structure requirements and cognitive rigor as enforced by DeBERTa classification, concept matching, and semantic duplicate validation.
