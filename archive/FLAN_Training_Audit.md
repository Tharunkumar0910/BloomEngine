# FLAN-T5 Training Audit

## 1. Training Format and Labels
Based on the generation prompt used in the system, the FLAN-T5 Base model was trained (or prompted) to perform dual-axis transformations. The input explicitly injects both cognitive and difficulty constraints:

**Input Format:**
```
Source Bloom: {source_bloom}
Source Difficulty: {source_diff}
Target Bloom: {target_bloom}
Target Difficulty: {target_diff}
Domain: {domain}
Topic: {topic}
Question: {question}
```
**Output:**
```
{Transformed Question}
```

## 2. Expected Capabilities
Because both `Target Bloom` and `Target Difficulty` are explicitly provided in the prompt, the model was expected to be capable of:
1. **Difficulty Transformation:** Scaling the complexity or depth of the question up or down.
2. **Bloom Transformation:** Shifting the verb and cognitive action to match a specific educational tier (e.g., from *Remember* to *Analyze*).

## 3. Is Bloom Drift Expected?
**Yes, severe Bloom Drift is entirely expected from the training format and model choice.** 

While the model was *trained/prompted* for both Bloom and Difficulty transformation, mapping 6 abstract cognitive levels (Remember, Understand, Apply, Analyze, Evaluate, Create) simultaneously with 3 Difficulty levels is an exceptionally complex semantic task. 
A 250M parameter model (FLAN-T5 Base) simply lacks the nuanced semantic reasoning and parameter volume required to reliably differentiate between overlapping cognitive boundaries (e.g., Apply vs. Analyze) in a zero-shot or lightly fine-tuned setting. The model often latches onto the general domain/topic and produces a generic "Moderate" question, ignoring the finer constraints of the prompt.

**Conclusion:** The generation failures are a known symptom of the model's architectural limitations, making the proposed Validation-Regeneration Pipeline the optimal solution to improve reliability without discarding the FLAN-T5 engine.
