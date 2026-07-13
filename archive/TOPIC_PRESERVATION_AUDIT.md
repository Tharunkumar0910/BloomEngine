# Topic Preservation Audit Report

This report provides a formal evaluation of topic and domain preservation across 90 generated question variants.

## Overall Statistics
- **Total Variants Evaluated:** 90
- **Topic Preservation Rate:** 80.00%
- **Domain Preservation Rate:** 82.22%
- **Bloom Accuracy:** 92.22%
- **Difficulty Accuracy:** 94.44%
- **Exact Match Rate:** 92.22%

### Failure Breakdown
| Failure Category | Count | Percentage |
|---|---|---|
| Topic Drift | 18 | 20.00% |
| Domain Drift | 15 | 16.67% |
| Bloom Drift | 5 | 5.56% |
| Difficulty Drift | 0 | 0.00% |
| Hallucination | 0 | 0.00% |

## Most Frequently Lost Concepts
| Concept keyword | Times Lost |
|---|---|
| auto scale | 9 |
| auto-scale | 9 |
| autoscal | 9 |
| normaliz | 4 |
| predict | 2 |
| analyt | 2 |
| denormaliz | 1 |
| agil | 1 |
| authenticat | 1 |
| firewall | 1 |

## Top 20 Failures
| # | Original Question | Target Diff | Generated Question | Lost Concepts | Failure Category |
|---|---|---|---|---|---|
| 1 | What is database indexing? | Easy | Analyze the performance impact of table indexing on query performance in a large scale database. | None | Bloom Drift |
| 2 | What is database indexing? | Difficult | Analyze how indexing affects query performance in large scale database systems. | None | Bloom Drift |
| 3 | Define normalization in DBMS. | Moderate | Analyze the log synchronization behavior and determine its influence on query performance. | normaliz, denormaliz | Topic Drift |
| 4 | What is a deadlock in an operating system? | Moderate | Analyze the execution behavior of a deadlock during the execution of msys. | None | Domain Drift |
| 5 | What is a deadlock in an operating system? | Difficult | Assess whether deadlocks are due to excessive resource allocation or to a poor execution performance. | None | Domain Drift |
| 6 | Explain Round Robin scheduling. | Moderate | In a Round Robin scheduler, why is it necessary to schedule a group of four patients for each round Robin session? | None | Domain Drift |
| 7 | Explain Round Robin scheduling. | Difficult | Identify the relationship between scheduling and rotation, and justify why it is more efficient than scheduling a round Robin during peak time. | None | Domain Drift |
| 8 | Define multi-factor authentication. | Easy | Explain how multi-factor authentication supports multi-user authentication, ensuring that every authentication is validated correctly. | None | Domain Drift |
| 9 | Define multi-factor authentication. | Moderate | Inspect the authentication procedures for a multi-factor authentication system and identify how each authentication method resolves the authentication issues. | None | Domain Drift |
| 10 | Define multi-factor authentication. | Difficult | Judge whether multi-factor authentication provides better authentication stability than the conventional key-to-key encryption. | None | Domain Drift |
| 11 | What is auto scaling in cloud computing? | Easy | Explain how scaling improves traffic coordination and recovery efficiency in enterprise cloud environments. | auto scale, auto-scale, autoscal | Topic Drift |
| 12 | What is auto scaling in cloud computing? | Moderate | Input a large-scale database query using the supplied workload and compute the scaling process. | auto scale, auto-scale, autoscal | Topic Drift |
| 13 | What is auto scaling in cloud computing? | Difficult | Assess whether automated scaling improves performance in a cloud-based enterprise system. | auto scale, auto-scale, autoscal | Topic Drift |
| 14 | Explain the purpose of a firewall. | Easy | Evaluate whether a firewall is effective for minimizing network congestion during the event that a server is compromised. | None | Bloom Drift |
| 15 | Explain the purpose of a firewall. | Moderate | Evaluate the effectiveness of firewall policies in protecting enterprise network privacy. | None | Bloom Drift |
| 16 | Define predictive analytics. | Easy | In order to identify potential data anomalies, identify potential sources of anomalies. | predict, analyt | Topic Drift |
| 17 | Apply normalization techniques to redesign a customer database schema. | Easy | Explain how a custom customer database schema can be reused with different databases. | normaliz | Topic Drift |
| 18 | Apply normalization techniques to redesign a customer database schema. | Moderate | Analyze the reordering process and determine how the schema fits with the customer's requirements. | normaliz | Topic Drift |
| 19 | Apply normalization techniques to redesign a customer database schema. | Difficult | Assess the schema design and identify the most efficient query model for a customer database schema. | normaliz | Topic Drift |
| 20 | Analyze the impact of deadlocks on system performance in a multitasking environment. | Easy | Recall the deadlock mechanism used in a multi-tasking environment and identify its causes. | None | Domain Drift |

## Root Cause Analysis
An analysis of the failures reveals the following key insights:
1. **Topic and Domain Drift:** Occurs when the generator (FLAN-T5 Base) is tasked with changing the Bloom level but fails to retain the technical noun phrases of the original question, replacing them with generic domain words.
2. **Bloom and Difficulty Drift:** Bloom levels (like Analyze vs. Apply) have overlapping cognitive boundaries that DeBERTa-v3 detects with varying confidence. When FLAN-T5 fails to use the exact prefix verbs, DeBERTa misclassifies them.
3. **Hallucination:** In rare cases, FLAN-T5 generates repeating sequences or empty outputs when the prompt length exceeds standard token sequences or when repetition penalties are not optimal.

## Recommendation
> [!IMPORTANT]
> **Determined Cause: D. Combination**
>
> While FLAN-T5 Base has parameter constraints that limit its semantic comprehension under high cognitive transformation demands (C), these are exacerbated by the prompt layout which lacks few-shot domain anchors (A), and validation parameters in `/rephrase` that score candidates strictly based on classifier prediction rather than enforcing topic keyphrase preservation (B).
