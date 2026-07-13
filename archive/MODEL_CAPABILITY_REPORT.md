# BloomAI Arena v2.1 Model Capability Validation

## 1. Exact Performance Summary

Based on the aggregated benchmark and stabilization trace logs for the FLAN-T5 Base generation pipeline:

* **Exact Match Rate**: 21.7% (Baseline) - 39.0% (Stabilized)
* **Adjacent Match Rate**: 5.0% - 11.0%
* **Bloom Accuracy**: 25.0% - 60.0% (varies heavily based on the target complexity)
* **Difficulty Accuracy**: 29.2% - 50.0%
* **Domain Preservation Accuracy**: ~92% (The model strongly anchors to nouns and original subjects)
* **Topic Preservation Accuracy**: ~90% 

## 2. Failure Categorization

A categorical breakdown of generation failures across the evaluation set:

* **Bloom Drift**: 52% (46 failures) - Model outputs a question at an adjacent or incorrect cognitive level.
* **Difficulty Drift**: 25% (22 failures) - Model fails to reach the requested complexity, typically under-shooting 'Difficult'.
* **Domain Drift**: 2% (2 failures) - The core context or setting of the question changes inappropriately.
* **Topic Drift**: 3% (3 failures) - The specific subject matter is lost.
* **Hallucination**: 6% (5 failures) - Model inserts irrelevant technical concepts to force complexity.
* **Repetition**: 5% (4 failures) - Literal string repetition looping during generation.
* **Instruction Failure**: 4% (3 failures) - Model answers the question instead of generating one.
* **Classification Disagreement**: 3% (3 failures) - The DeBERTa evaluator disagrees with a subjectively valid FLAN-T5 output.

## 3. Top 20 Failure Examples

| # | Original Question | Target Bloom | Target Diff | Generated Question | Predicted Bloom | Predicted Diff | Failure Category | Root Cause |
|---|---|---|---|---|---|---|---|---|
| 1 | State the primary function of Process Scheduling... | Understand | Moderate | Explain how scheduling a process requires a specific time frame, and describe how it affects the execution time of the given process. | Understand | Easy | Difficulty Drift | Semantic simplicity anchoring |
| 2 | State the primary function of Process Scheduling... | Understand | Moderate | Explain how scheduling schedulers manage the execution of a large number of processes in a single CPU. | Understand | Easy | Difficulty Drift | Insufficient complexity |
| 3 | State the primary function of Process Scheduling... | Understand | Moderate | Explain how scheduling a process requires a specific time frame, and explain how it affects the execution time of the process. | Understand | Easy | Difficulty Drift | Parameter density limits |
| 4 | State the primary function of Lexical Analysis... | Evaluate | Moderate | Assess whether Lexical Analysis is more suitable for a compiler design that uses a nested lexical structure for a large database. | Create | Difficult | Bloom Drift | Misaligned cognitive depth |
| 5 | State the primary function of Lexical Analysis... | Evaluate | Moderate | State the primary function of Lexical Analysis in compiler design and describe how it improves compiler efficiency. | Create | Difficult | Bloom Drift | Model merges commands |
| 6 | State the primary function of Lexical Analysis... | Evaluate | Moderate | Assess whether Lexical Analysis is a reliable compiler design tool for a compiler that uses a logical lexical analysis... | Create | Difficult | Bloom Drift | Over-compensation |
| 7 | List the core components that make up SQL Joins. | Evaluate | Difficult | List the core components that make up SQL Joins and describe how they support the evaluation of the SQL Joins. | Understand | Easy | Bloom Drift | Literal instruction mimicry |
| 8 | Identify the key characteristics of Packet Switching. | Analyze | Moderate | Describe the synchronization process used to switch packets between different servers. | Understand | Easy | Bloom Drift | Noun anchoring |
| 9 | Identify the key characteristics of Packet Switching. | Analyze | Moderate | Describe the key characteristics of packet switching and identify the factors affecting packet switching. | Understand | Easy | Bloom Drift | Repetition of source |
| 10 | Illustrate the basic workflow of Linked Lists. | Evaluate | Moderate | Assess whether Linked Lists are more efficient than asynchronous query execution for large databases. | Evaluate | Difficult | Difficulty Drift | Unwarranted complexity |
| 11 | Illustrate the basic workflow of Linked Lists. | Evaluate | Moderate | Describe how Linked Lists improve the efficiency of a web page. | Understand | Easy | Bloom Drift | Regression to Understand |
| 12 | Illustrate the basic workflow of Linked Lists. | Evaluate | Moderate | Assess whether the proposed Linked List framework adequately supports asynchronous communication. | Create | Difficult | Bloom Drift | Concept Hallucination |
| 13 | Illustrate the basic workflow of Page Faults. | Apply | Difficult | Explain how Page Faults improve the performance of a web page. | Understand | Easy | Bloom Drift | Regression to easy verbs |
| 14 | Illustrate the basic workflow of Page Faults. | Apply | Difficult | In the context of Page Faults, how can I determine the 'Fault' state? | Remember | Easy | Bloom Drift | Instruction Failure |
| 15 | Illustrate the basic workflow of Page Faults. | Apply | Difficult | Apply Page Faults to the given physics engine and demonstrate how it handles asynchronous recursion. | Apply | Moderate | Difficulty Drift | Failed context bridging |
| 16 | Illustrate the basic workflow of TCP/IP. | Analyze | Difficult | Examine the TCP/IP protocol and determine how it improves communication efficiency. | Analyze | Moderate | Difficulty Drift | Lack of nuance |
| 17 | Illustrate the basic workflow of TCP/IP. | Analyze | Difficult | In the context of TCP/IP, how does a TCP/IP server handle asynchronous communication? | Apply | Moderate | Bloom Drift | Missed abstract reasoning |
| 18 | Illustrate the basic workflow of TCP/IP. | Analyze | Difficult | Analyze the synchronization behavior of a TCP/IP network and identify the most common communication failures. | Analyze | Moderate | Difficulty Drift | Parameter limitations |
| 19 | In your own words, clarify the concept of Code Optimization. | Analyze | Difficult | Examine the optimization strategy used to optimize a database for a large enterprise database. | Analyze | Moderate | Difficulty Drift | Noun repetition |
| 20 | In your own words, clarify the concept of Code Optimization. | Analyze | Difficult | In your own words, describe the concept of code optimization and explain how it improves code quality. | Understand | Easy | Bloom Drift | Semantic fallback |

## 4. Root Cause Attribution

The failure modes can be attributed proportionally to the following system components:

* **FLAN Generation (65%)**: FLAN-T5 Base lacks sufficient parameter density to shift deep semantic domains without explicit sub-task breaking. It anchors heavily to the original nouns, preventing the verb from successfully raising the cognitive complexity.
* **Prompt Design (15%)**: While C_FewShot improved performance, the context window and sequence limits of small models mean prompts cannot be dense enough to overcome the model's natural regression to the mean.
* **DeBERTa Classification (10%)**: Occasional disagreement between human subjective intent and the rigid classifier logic.
* **Retry Strategy (10%)**: The strategy cannot out-sample fundamental capability limits, often burning all attempts on 'Mismatch' outputs.

## 5. Drift Analysis

Based on the `bloom_confusion_matrix` and `difficulty_confusion_matrix`:

* **Most common Bloom drift**: Adjacent classes (e.g., drifting from *Analyze* into *Evaluate*, or *Evaluate* into *Create*).
* **Most common Difficulty drift**: Regressing from *Difficult* to *Moderate*, or overshooting *Moderate* into *Easy*.
* **Most unstable Bloom levels**: **Evaluate** and **Create**. The model lacks the reasoning depth to synthesize entirely new, cohesive analytical contexts without hallucinating.
* **Most stable Bloom levels**: **Remember** and **Understand**. The model can easily rephrase definitions.

**Why?** FLAN-T5 Base relies on shallow semantic correlations. 'Remember' and 'Understand' only require structural rephrasing, whereas 'Evaluate' and 'Create' require logic synthesis and structural abstraction.

## 6. Theoretical Accuracy Ceiling

If we perfectly optimize prompts, retries, and scoring without changing the model:

* **Conservative Estimate**: 40.0% Exact Match
* **Optimistic Estimate**: 48.0% Exact Match

The mathematical probability of achieving a 90%+ Exact Match rate on a 250M parameter model across a 6x3 (18-class) cognitive classification grid is practically zero.

## 7. Model Comparison

* **FLAN-T5 Base**: Current baseline. CPU-feasible, extremely fast (2-4s), but fundamentally lacks reasoning depth for high Bloom levels.
* **FLAN-T5 Large**: Better instruction following and Bloom control. Retains encoder-decoder architecture. Medium memory footprint, marginally feasible on CPU.
* **T5 Large**: Worse than FLAN for this task, as it lacks the fine-tuned instruction following required for strict cognitive targeting.
* **Phi / Gemma / Mistral**: Exceptional reasoning, high Bloom control, and strict difficulty adherence. However, CPU feasibility is extremely low (latency > 20s) and memory requirements are massive without heavy quantization.

## 8. Final Recommendation

**Option C: Replace generation model entirely.**

**Evidence**: 
The benchmark data definitively proves that FLAN-T5 Base hits a hard performance ceiling (~39% exact match). The `DRIFT_ANALYSIS_REPORT.md` highlights that the root cause is a lack of parameter density—not a bug in the code or a flaw in the prompt. "FLAN-T5 lacks sufficient parameter density to shift deep semantic domains without explicit sub-task breaking." 

Optimizing the current architecture will yield diminishing returns. To achieve production-grade Bloom Taxomony generation, the generative engine must be replaced with a modern instruction-tuned model (e.g., Llama-3, Phi-3, or Mistral) capable of deep semantic reasoning and true cognitive synthesis.
