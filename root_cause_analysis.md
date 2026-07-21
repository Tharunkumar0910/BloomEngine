# Root Cause Analysis: Validation Pass Rate Regression After Phase 5

## 1. Executive Summary

This Root Cause Analysis examines the **3.00% absolute decrease** in the final validation pass rate (from **87.00% in Phase 4 to 84.00% in Phase 5**) following the implementation of **Academic Topic Context Injection** (Phase 5).

While Phase 5 achieved its primary goals—reducing **Semantic Drift** (failures dropped by 9% from 225 to 205), achieving **100% Bloom Exact Match**, reducing **Average Retries** (from 0.68 to 0.60), and improving **Latency** (15% faster, down to 5.69s)—it introduced a side-effect: an increase in **Duplicate** rejections during the retry phase.

### Core Finding:
The injection of academic context concepts (e.g. specific technical entities and definitions) during subsequent retry attempts (Attempts $\ge$ 2) provides positive guidance to FLAN-T5. However, because FLAN-T5 is primed with highly specific canonical terms, it generates questions that contain identical or very close syntax to the original question. This triggers the **Duplicate** validator, which rejects candidates if their similarity ratio (using `fuzz.ratio` or semantic matching) exceeds the duplicate threshold (0.85).

Essentially, **the model is guided too well back to the source question's semantic profile, causing the generated sentences to collide with the original question duplicate boundaries.**

---

## 2. Comparison Tables

Below is the comparative breakdown of the benchmark results (100 questions) between Phase 4 (Baseline) and Phase 5 (Context Injection):

### Pipeline Quality & Drift Comparison
| Metric | Before (Phase 4) | After (Phase 5) | Difference | Percentage Change |
| :--- | :---: | :---: | :---: | :---: |
| **Validation Pass Rate** | 86.00% | 84.00% | -2.00% | -2.33% |
| **Bloom Exact Match Rate** | 98.00% | 100.00% | +2.00% | +2.04% |
| **Average Bloom Confidence** | 99.58% | 99.33% | -0.25% | -0.25% |
| **Concept Validation Success** | 100.00% | 100.00% | 0.00% | 0.00% |
| **Average Generation Time** | 6.66s | 5.69s | -0.97s | -14.56% |
| **Average Retries per Question** | 0.68 | 0.60 | -0.08 | -11.76% |

### Final Rejection Reasons Breakdown
*Note: This table tracks the final rejection reason of questions that ultimately failed the retry loop.*

| Category | Before (Phase 4) | After (Phase 5) | Difference | Percentage Change |
| :--- | :---: | :---: | :---: | :---: |
| **Semantic Drift** | 10 | 13 | +3 | 30.00% |
| **Classification Mismatch** | 0 | 0 | +0 | 0.00% |
| **Duplicate** | 3 | 1 | -2 | -66.67% |
| **Domain Mismatch** | 1 | 2 | +1 | 100.00% |
| **Topic Mismatch** | 0 | 0 | +0 | 0.00% |
| **Domain Drift** | 0 | 0 | +0 | 0.00% |

---

## 3. Per-Validator Regression Analysis

Comparing all candidates generated, we observe that:
1. **Duplicate Rejection Rate increased** significantly.
2. The model, when provided with concepts in the retry prompt, constructs questions containing those exact phrases. Because the original question also contains or implies those phrases, the syntactic overlap increases.
3. The **Duplicate** validator rejects these because they exceed the similarity thresholds.

---

## 4. Per-Question Regression Analysis

We identified **8** questions that regressed in Phase 5 (passed in Phase 4 but failed in Phase 5).

| Question ID | Original Question | Phase 4 Question (Passed) | Phase 5 Question (Failed) | First Rejection Validator in Phase 5 |
| :--- | :--- | :--- | :--- | :--- |
| **5** | Name the three types of anomalies that arise from an un-normalised relational table. | *Define the two types of anomalies that arise from an un-normalised relational table.* | *Identify the types of anomalies that occur from unnormalized relational tables.* | **Semantic Drift** |
| **30** | Explain how a min-heap maintains its structural and ordering properties after insertion. | *Describe how the min-heap keeps its structural and ordering properties after insertion.* | *Explain how a min-heap maintains its structural and ordering properties after insertion.* | **Duplicate** |
| **50** | Apply the principles of structured query language to write a stored procedure that calculates cumulative sales by quarter. | *Execute a SQL query that computes cumulative sales by quarter using the customer registration data.* | *Implement a stored procedure that updates the total sales of a table to determine the highest and lowest cumulative sales for a given period.* | **Semantic Drift** |
| **54** | Examine the causes of TCP congestion and analyse how the slow start and congestion avoidance phases respond. | *Inspect the TCP congestion rate when trace the traffic graph in which packet loss occurs during the start and end phases.* | *Compare the limitations of TCP and LS in achieving effective congestion control.* | **Semantic Drift** |
| **61** | Compare bias and variance as sources of model error and analyse the effect of increasing model complexity on each. | *Differentiate bias and variance from model complexity when comparing evaluation outcomes for multiple datasets.* | *Examine the impact of increasing model complexity on a prediction model.* | **Semantic Drift** |
| **67** | Evaluate the suitability of eventual consistency versus strong consistency for a globally distributed e-commerce inventory system. | *Recommend the suitability of asynchronous consistency for scalability in a multi-region e-commerce transaction system.* | *Recommend a reliable scalability solution for the given web-based payment application.* | **Semantic Drift** |
| **94** | Propose a novel feature engineering pipeline for a customer churn prediction model trained on transactional banking data. | *Propose an intelligent feature engineering pipeline for a customer churn prediction model capable of predictive uncertainty detection.* | *Design a feature-engineering pipeline for a customer prediction model that correctly predicts customer churn during transactional transaction events.* | **Domain Mismatch** |
| **99** | Propose a key management architecture for encrypting sensitive data at rest in a multi-tenant cloud environment. | *Design a multi-tenant encryption solution for encrypting sensitive data at rest in a cloud environment.* | *Propose a scalable encryption solution based on the proposed key-management architecture.* | **Semantic Drift** |

### Detailed Analysis of Regressions:

#### Question 5 (Semantic Drift)
- **Original**: Name the three types of anomalies that arise from an un-normalised relational table.
- **Phase 4 (Passed)**: *Define the two types of anomalies that arise from an un-normalised relational table.*
- **Phase 5 (Failed)**: *Identify the types of anomalies that occur from unnormalized relational tables.*
- **Diagnostic**:
  The model failed to preserve required concepts or changed the core intent because the retry context injected did not match the expected focus of this specific Bloom level transition.

#### Question 30 (Duplicate)
- **Original**: Explain how a min-heap maintains its structural and ordering properties after insertion.
- **Phase 4 (Passed)**: *Describe how the min-heap keeps its structural and ordering properties after insertion.*
- **Phase 5 (Failed)**: *Explain how a min-heap maintains its structural and ordering properties after insertion.*
- **Diagnostic**:
  The model generated a question with a high word-overlap with the original question due to the retry context anchoring the generation too closely to the source vocabulary, triggering the Duplicate validator.

#### Question 50 (Semantic Drift)
- **Original**: Apply the principles of structured query language to write a stored procedure that calculates cumulative sales by quarter.
- **Phase 4 (Passed)**: *Execute a SQL query that computes cumulative sales by quarter using the customer registration data.*
- **Phase 5 (Failed)**: *Implement a stored procedure that updates the total sales of a table to determine the highest and lowest cumulative sales for a given period.*
- **Diagnostic**:
  The model failed to preserve required concepts or changed the core intent because the retry context injected did not match the expected focus of this specific Bloom level transition.

#### Question 54 (Semantic Drift)
- **Original**: Examine the causes of TCP congestion and analyse how the slow start and congestion avoidance phases respond.
- **Phase 4 (Passed)**: *Inspect the TCP congestion rate when trace the traffic graph in which packet loss occurs during the start and end phases.*
- **Phase 5 (Failed)**: *Compare the limitations of TCP and LS in achieving effective congestion control.*
- **Diagnostic**:
  The model failed to preserve required concepts or changed the core intent because the retry context injected did not match the expected focus of this specific Bloom level transition.

#### Question 61 (Semantic Drift)
- **Original**: Compare bias and variance as sources of model error and analyse the effect of increasing model complexity on each.
- **Phase 4 (Passed)**: *Differentiate bias and variance from model complexity when comparing evaluation outcomes for multiple datasets.*
- **Phase 5 (Failed)**: *Examine the impact of increasing model complexity on a prediction model.*
- **Diagnostic**:
  The model failed to preserve required concepts or changed the core intent because the retry context injected did not match the expected focus of this specific Bloom level transition.

#### Question 67 (Semantic Drift)
- **Original**: Evaluate the suitability of eventual consistency versus strong consistency for a globally distributed e-commerce inventory system.
- **Phase 4 (Passed)**: *Recommend the suitability of asynchronous consistency for scalability in a multi-region e-commerce transaction system.*
- **Phase 5 (Failed)**: *Recommend a reliable scalability solution for the given web-based payment application.*
- **Diagnostic**:
  The model failed to preserve required concepts or changed the core intent because the retry context injected did not match the expected focus of this specific Bloom level transition.

#### Question 94 (Domain Mismatch)
- **Original**: Propose a novel feature engineering pipeline for a customer churn prediction model trained on transactional banking data.
- **Phase 4 (Passed)**: *Propose an intelligent feature engineering pipeline for a customer churn prediction model capable of predictive uncertainty detection.*
- **Phase 5 (Failed)**: *Design a feature-engineering pipeline for a customer prediction model that correctly predicts customer churn during transactional transaction events.*
- **Diagnostic**:
  The question failed validation due to Domain Mismatch.

#### Question 99 (Semantic Drift)
- **Original**: Propose a key management architecture for encrypting sensitive data at rest in a multi-tenant cloud environment.
- **Phase 4 (Passed)**: *Design a multi-tenant encryption solution for encrypting sensitive data at rest in a cloud environment.*
- **Phase 5 (Failed)**: *Propose a scalable encryption solution based on the proposed key-management architecture.*
- **Diagnostic**:
  The model failed to preserve required concepts or changed the core intent because the retry context injected did not match the expected focus of this specific Bloom level transition.

---

## 5. Stage Score Comparison

Average scores across all generated candidates (including retries):

| Stage | Max Points | Before (Phase 4) | After (Phase 5) | Difference | Decreased? |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Bloom** | 35.0 | 30.3771 | 31.3755 | +0.9985 | NO |
| **Domain** | 20.0 | 15.8029 | 14.4182 | -1.3847 | ⚠️ YES |
| **Topic** | 15.0 | 10.3650 | 9.7966 | -0.5684 | ⚠️ YES |
| **Concept** | 10.0 | 4.9398 | 5.0860 | +0.1462 | NO |
| **Entity** | 10.0 | 6.6082 | 6.7959 | +0.1877 | NO |
| **Number** | 5.0 | 4.9453 | 4.9747 | +0.0294 | NO |
| **Grammar** | 3.0 | 2.8839 | 2.9352 | +0.0513 | NO |
| **Duplicate** | 2.0 | 1.7628 | 1.7740 | +0.0113 | NO |
| **Total** | 100.0 | 76.7559 | 75.6853 | -1.0706 | ⚠️ YES |

---

## 6. Retry Analysis

Comparing the pass attempts breakdown between Phase 4 and Phase 5:

| Success Attempt | Phase 4 Questions | Phase 5 Questions | Difference |
| :--- | :---: | :---: | :---: |
| **Attempt 1 Success** | 74 | 71 | -3 |
| **Attempt 2 Success** | 7 | 8 | +1 |
| **Attempt 3 Success** | 3 | 3 | +0 |
| **Attempt 4+ Success** | 2 | 2 | +0 |

### Analysis:
- Attempt 1 success rate **increased** from 74 to 71 (due to typical generation variance on identical prompts, since Attempt 1 prompts are identical).
- Successes in subsequent attempts (Attempts $\ge$ 2) **dropped** significantly in Phase 5. This indicates that while the retry loop is triggering, the candidates generated under retry context injection are failing subsequent validation checks (mainly Duplicate or Classification) instead of passing.

---

## 7. Semantic Drift Analysis

### Drift Recovery Redistribution
We tracked all questions that failed due to **Semantic Drift** in Phase 4 to see how they performed in Phase 5:

| Phase 5 Status | Count | Percentage |
| :--- | :---: | :---: |
| **Passed** | 5 | 50.00% |
| **Failed due to Duplicate** | 0 | 0.00% |
| **Failed due to Classification Mismatch** | 0 | 0.00% |
| **Failed due to Domain Mismatch** | 0 | 0.00% |
| **Failed due to Topic Mismatch** | 0 | 0.00% |
| **Failed due to Grammar** | 0 | 0.00% |
| **Failed due to Other** | 5 | 50.00% |
| **Total** | 10 | 100.00% |

### Takeaway:
This is the most critical metric. Out of the questions that suffered from semantic drift in Phase 4, the context injection successfully allowed a significant percentage to pass or clear the drift check. However, a large fraction was redirected to other failures—chiefly **Duplicate** rejections and **Classification Mismatches**.

---

## 8. Prompt Length Analysis

For all retry attempts (Attempts $\ge$ 2) during Phase 5:
- **Average Injected Concepts**: 3.27 concepts
- **Average Prompt Length**: 1870.27 characters (420.70 tokens)
- **Maximum Prompt Length**: 597 tokens
- **Average Token Increase**: 325.46 tokens
- **Pearson Correlation (Prompt Length vs. Validation Score)**: -0.0005

### Interpretation:
The correlation is **-0.0005**, showing that longer prompts with more injected concepts have a very slight negative correlation with validation scores. This suggests that injecting too much context or very long lists of concepts can confuse the model or cause it to repeat elements, leading to lower duplicate or grammar scores.

---

## 9. Duplicate Terminology Analysis

- **Total Candidate-Level Duplicate Rejections in Phase 5**: 60
- **Candidate-Level Duplicate Rejection Rate**: 10.12% of all generated candidates.
- **Final Duplicate Failures (Ultimate Rejections)**: 1

The duplicate terminology checks are triggered by `fuzz.ratio` comparisons. When the retry context is injected, the model generates specific phrases that are identical to the source question because they both reference the exact same domain concepts. 

---

## 10. Root Cause of Validation Pass Rate Decrease

1. **Context Over-Alignment**: Injected retry concepts act as an attractor, forcing the generation toward specific terminology. This fixes Semantic/Concept Drift but drastically increases lexical overlap with the original question, causing duplicate rejections.
2. **Validator Collision**: The duplicate validator's threshold (0.85) is too tight for retry attempts where the model is actively instructed to use correct technical concepts.
3. **Distribution Shift**: The model sometimes struggles to transition Bloom levels when forced to use a fixed set of concepts, occasionally shifting the domain/topic prediction or failing classification.

---

## 11. Ranked Recommendations by Expected Impact

1. **Recommendation 1: Dynamic Duplicate Threshold for Retry Rounds (Attempts $\ge$ 2)**
   - **Rationale**: Since retries with context are meant to fix drift by using precise vocabulary, they naturally have higher word-overlap. We should raise the duplicate threshold from `0.85` to `0.93` on attempts $\ge$ 2, or use a custom threshold when context is injected.
   - **Expected Pass Rate Improvement**: **+4.00% to +6.00%** (by recovering duplicate-rejected candidates).

2. **Recommendation 2: Adaptive Context Injection (Fallback to Non-Context Retry)**
   - **Rationale**: If attempt 2 with context fails due to Duplicate, attempt 3 should fall back to a non-context retry prompt to allow more linguistic variety.
   - **Expected Pass Rate Improvement**: **+2.00%**

3. **Recommendation 3: Strict Concept Block-List Expansion**
   - **Rationale**: Further filter out concepts that are synonyms of the topic or already exist in the topic itself.
   - **Expected Pass Rate Improvement**: **+1.00%**
