# BloomAI Arena v2.1 Mode E Evaluation Report

## Executive Summary

This report evaluates the performance of **Mode E (Multi-Candidate Ranking)** against the production baseline **Mode B (Production)**. Mode E introduces a multi-candidate generation strategy returning up to 5 candidates per FLAN-T5 call and performing ranking-based selection, whereas Mode B runs a sequential retry-until-success strategy. Both modes are evaluated on identical questions, templates, validation parameters, and models.

> [!WARNING]
> **Recommendation:** **REJECT OR REWRITE**. Mode E failed to meet one or more success criteria. Do not promote Mode E to production default without addressing the failures.

## Adoption Success Criteria Checklist

- **Bloom Accuracy (>= Mode B):** ❌ FAILED (Mode E: 96.7% vs Mode B: 100.0%)
- **Difficulty Accuracy (>= Mode B):** ❌ FAILED (Mode E: 96.7% vs Mode B: 100.0%)
- **Overall Pass Rate (>= Mode B):** ❌ FAILED (Mode E: 96.7% vs Mode B: 100.0%)
- **Concept Preservation (>= Mode B):** ✅ MET (Mode E: 100.0% vs Mode B: 100.0%)
- **First Attempt Success Rate (>= Mode B):** ❌ FAILED (Mode E: 80.0% vs Mode B: 96.7%)
- **Average Generation Time (>= 20% lower):** ❌ FAILED (Mode E: 2.55s vs Mode B: 3.09s)
- **Average FLAN Calls (lower than Mode B):** ✅ MET (Mode E: 1.03 vs Mode B: 1.07)
- **Failure Rate (does not increase):** ❌ FAILED (Mode E: 3.3% vs Mode B: 0.0%)

## Detailed Metric Comparison Table

| Metric | Mode B (Production) | Mode E (Multi-Candidate) | Difference | Status |
|---|---|---|---|---|
| First Attempt Success Rate | 96.7 | 80.0 | -16.70% | FAIL |
| Second Attempt Success Rate | 0.0 | 0.0 | +0.00% | PASS |
| Accepted After Retry | 3.3 | 0.0 | -3.30% | FAIL |
| Failed After Retry | 0.0 | 3.3 | +3.30% | PASS |
| Overall Pass Rate | 100.0 | 96.7 | -3.30% | FAIL |
| Bloom Accuracy | 100.0 | 96.7 | -3.30% | FAIL |
| Difficulty Accuracy | 100.0 | 96.7 | -3.30% | FAIL |
| Bloom Macro F1 | 1.0 | 0.982 | -0.018 | FAIL |
| Concept Preservation | 100.0 | 100.0 | +0.00% | PASS |
| Average Confidence | 100.0 | 100.0 | +0.00% | PASS |
| Average FLAN Calls | 1.07 | 1.03 | -0.04 | PASS |
| Average Generation Time (s) | 3.09 | 2.55 | -0.54 | FAIL |
| Duplicate Rate | 0.0 | 0.0 | +0.00% | PASS |
| Failure Rate | 0.0 | 3.3 | +3.30% | FAIL |

## Mode E Execution Call Statistics

These metrics track candidates processed in the pipeline:
- **Average Candidates Generated per Variant:** 3.10
- **Average Candidates Validated (DeBERTa Calls) per Variant:** 1.03
- **Average Candidates Deduplicated (Rejected Before Validation) per Variant:** 0.27

## Bloom-Level Performance Analysis

### Per-Bloom Level Accuracy Comparison
| Bloom Level | Mode B Accuracy | Mode E Accuracy | Difference |
|---|---|---|---|
| Remember | 100.0% | 80.0% | -20.0% |
| Understand | 100.0% | 100.0% | +0.0% |
| Apply | 100.0% | 100.0% | +0.0% |
| Analyze | 100.0% | 100.0% | +0.0% |
| Evaluate | 100.0% | 100.0% | +0.0% |
| Create | 100.0% | 100.0% | +0.0% |

### Transformation Pair Analysis
This section tracks how questions migrate across cognitive transitions. Below are the pass rates for specific Bloom level target mappings:

| Transition | Mode B Pass Rate | Mode E Pass Rate | Difference |
|---|---|---|---|
| Remember &rarr; Understand | 100.0% | 100.0% | +0.0% |
| Remember &rarr; Apply | 100.0% | 100.0% | +0.0% |
| Remember &rarr; Analyze | 100.0% | 100.0% | +0.0% |
| Remember &rarr; Evaluate | 100.0% | 100.0% | +0.0% |
| Remember &rarr; Create | 100.0% | 100.0% | +0.0% |
| Understand &rarr; Remember | 100.0% | 80.0% | -20.0% |
| Understand &rarr; Apply | 100.0% | 100.0% | +0.0% |
| Understand &rarr; Analyze | 100.0% | 100.0% | +0.0% |
| Understand &rarr; Evaluate | 100.0% | 100.0% | +0.0% |
| Understand &rarr; Create | 100.0% | 100.0% | +0.0% |
| Apply &rarr; Remember | 100.0% | 80.0% | -20.0% |
| Apply &rarr; Understand | 100.0% | 100.0% | +0.0% |
| Apply &rarr; Analyze | 100.0% | 100.0% | +0.0% |
| Apply &rarr; Evaluate | 100.0% | 100.0% | +0.0% |
| Apply &rarr; Create | 100.0% | 100.0% | +0.0% |
| Analyze &rarr; Remember | 100.0% | 80.0% | -20.0% |
| Analyze &rarr; Understand | 100.0% | 100.0% | +0.0% |
| Analyze &rarr; Apply | 100.0% | 100.0% | +0.0% |
| Analyze &rarr; Evaluate | 100.0% | 100.0% | +0.0% |
| Analyze &rarr; Create | 100.0% | 100.0% | +0.0% |
| Evaluate &rarr; Remember | 100.0% | 80.0% | -20.0% |
| Evaluate &rarr; Understand | 100.0% | 100.0% | +0.0% |
| Evaluate &rarr; Apply | 100.0% | 100.0% | +0.0% |
| Evaluate &rarr; Analyze | 100.0% | 100.0% | +0.0% |
| Evaluate &rarr; Create | 100.0% | 100.0% | +0.0% |
| Create &rarr; Remember | 100.0% | 80.0% | -20.0% |
| Create &rarr; Understand | 100.0% | 100.0% | +0.0% |
| Create &rarr; Apply | 100.0% | 100.0% | +0.0% |
| Create &rarr; Analyze | 100.0% | 100.0% | +0.0% |
| Create &rarr; Evaluate | 100.0% | 100.0% | +0.0% |

## Rejection Reason Distribution

| Rejection Reason | Mode B Count | Mode E Count | Mode B % | Mode E % |
|---|---|---|---|---|
| Too Short | 0 | 1 | 0.0% | 100.0% |

## Prompt Cost Analysis

| Mode | Prompt Tokens | Completion Tokens | Total Tokens | Cost Factor |
|---|---|---|---|---|
| Mode B (Production) | 180.9 | 18.0 | 198.9 | 1.0x |
| Mode E (Multi-Candidate Ranking) | 202.8 | 19.1 | 221.8 | 1.12x |

## First Attempt Analysis

- **Mode B (Production):** Succeeded on the first attempt for 29/30 question variants (96.7%).
- **Mode E (Multi-Candidate Ranking):** Succeeded on the first attempt for 24/30 question variants (80.0%).

## Manual Review Summary

Comparison of generated outputs indicates the following distribution of preferred variants:
- **Mode B:** preferred in 14/30 runs (46.7%).
- **Tie:** preferred in 10/30 runs (33.3%).
- **Mode E:** preferred in 6/30 runs (20.0%).

Detailed comparisons are recorded in `generation_comparison.csv` and `manual_review.csv`.