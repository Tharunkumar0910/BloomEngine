# BloomEngine

<p align="center">
  <img src="static/images/logo/bloomengine-logo.png" alt="BloomEngine Logo" width="200" />
</p>

<p align="center">
  <strong>AI-Powered Bloom's Taxonomy Question Transformation Engine</strong><br/>
  <em>MCA Major Project — Fine-tuned NLP Pipeline for Cognitive-Level Question Generation</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Flask-3.0.x-black?logo=flask&logoColor=white" />
  <img src="https://img.shields.io/badge/PyTorch-2.x-orange?logo=pytorch&logoColor=white" />
  <img src="https://img.shields.io/badge/HuggingFace-Transformers-yellow?logo=huggingface&logoColor=white" />
  <img src="https://img.shields.io/badge/spaCy-3.x-blueviolet" />
  <img src="https://img.shields.io/badge/DeBERTa--v3-Classifier-informational" />
  <img src="https://img.shields.io/badge/FLAN--T5-Generator-success" />
  <img src="https://img.shields.io/badge/Tests-36%20Passed-brightgreen" />
  <img src="https://img.shields.io/badge/Version-2.1.0-blue" />
  <img src="https://img.shields.io/badge/License-MIT-lightgrey" />
</p>

---

## What is BloomEngine?

**BloomEngine** is a full-stack AI question transformation system built as an MCA Major Project. It takes an input question at any Bloom's Taxonomy cognitive level and rewrites it into a target cognitive level — **Remember → Understand → Apply → Analyze → Evaluate → Create** — while rigorously preserving all original concepts, technical entities, numeric values, and semantic meaning.

The system is powered by two locally fine-tuned transformer models:
- **DeBERTa-v3** — 6-class Bloom's Taxonomy classifier (fine-tuned on 31,310 CS question records)
- **FLAN-T5** — Instruction-tuned seq2seq generator (fine-tuned on 21,004 question transformation pairs)

Every generated question passes through an **8-stage NLP validation pipeline** before being presented as output.

---

## System Architecture

```
[User Input Question]
        │
        ▼
[DeBERTa-v3 Bloom Classifier]   ←── Classifies input cognitive level (99.99% confidence)
        │
        ▼
[Question Understanding Engine] ←── Domain inference, topic mapping, concept extraction
        │
        ▼
[FLAN-T5 Multi-Candidate Generator] ←── Generates 3–6 candidate variants per round
        │
        ▼
[8-Stage Validation Pipeline]
  ├── Stage 1 : Bloom Validator          (verb profiling, target-level alignment)
  ├── Stage 2 : Concept Validator        (spaCy noun chunks, compound noun preservation)
  ├── Stage 3 : Technical Entity Validator (NER, tech jargon, CS terminology)
  ├── Stage 4 : Number Validator         (IPv4/IPv6, AES-128, version strings)
  ├── Stage 5 : Knowledge Consistency    (concept graph, domain-topic scoring)
  ├── Stage 6 : Semantic Validator       (SentenceTransformer cosine similarity ≥ 70%)
  ├── Stage 7 : Duplicate Detector       (SequenceMatcher + semantic distance)
  └── Stage 8 : Grammar Validator        (punctuation, length, bigram repetition)
        │
        ▼
[Candidate Ranker]  ←── Scores and selects the best candidate
        │
        ▼
[Final Validated Question Output]
```

---

## Key Metrics

| Metric | Value |
|--------|-------|
| Bloom Classification Accuracy | **99.99%** confidence (DeBERTa-v3) |
| Classification Dataset | **31,310** CS question records |
| Transformation Dataset | **21,004** question pairs |
| Evaluation Benchmark | **300-item** benchmark dataset |
| Validation Pass Rate | ≥ **88%** overall |
| Python Unit Tests | **36/36 passed** |
| Production API Checks | **6/6 passed** |
| Pipeline Version | **v2.1.0** |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.12, Flask |
| **AI — Classifier** | DeBERTa-v3 (fine-tuned, 6-class Bloom taxonomy) |
| **AI — Generator** | FLAN-T5 (fine-tuned, seq2seq question transformation) |
| **NLP** | spaCy `en_core_web_sm`, SentenceTransformers |
| **String Matching** | RapidFuzz (fuzzy duplicate detection) |
| **Frontend** | HTML5, CSS3, Vanilla JS, Chart.js |
| **Testing** | pytest (unit), Playwright (E2E) |
| **Inference** | PyTorch, Hugging Face Transformers |

---

## 8-Stage Validation Pipeline

| Stage | Validator | Purpose |
|-------|-----------|---------|
| 1 | **Bloom Validator** | Ensures generated verbs and sentence structure match the target Bloom level |
| 2 | **Concept Validator** | Extracts noun chunks from source and verifies they appear in the output |
| 3 | **Technical Entity Validator** | Protects CS-specific terms (SQL, TCP, IPv4, AES, etc.) from being dropped or mutated |
| 4 | **Number Validator** | Matches numeric values, version strings, protocol identifiers (AES-128, IPv6, 802.11) |
| 5 | **Knowledge Consistency Validator** | Domain-topic scoring via concept graph with position, frequency, and centrality weighting |
| 6 | **Semantic Validator** | SentenceTransformer cosine similarity ≥ 70% between source and output |
| 7 | **Duplicate Detector** | Blocks structurally or semantically near-identical outputs within session history |
| 8 | **Grammar Validator** | Capitalization, punctuation, length bounds, and bigram repetition checks |

**Scoring weights (config.py):**

```
Bloom        35 pts | Knowledge Domain  20 pts | Topic       15 pts
Concept      10 pts | Entity            10 pts | Number       5 pts
Grammar       3 pts | Duplicate          2 pts
Pass threshold: 80 / 100
```

---

## Repository Structure

```
BloomAI_Arena_v2_1/
├── app.py                      # Flask server — REST API endpoints & request routing
├── config.py                   # All hyperparameters, thresholds, Bloom profiles, validation weights
├── requirements.txt            # Python dependencies
├── playwright.config.js        # Playwright E2E test configuration
│
├── models/                     # Fine-tuned model weights (tracked via Git LFS)
│   ├── classifier/             # DeBERTa-v3 Bloom classifier
│   │   ├── config.json
│   │   ├── tokenizer.json
│   │   ├── spm.model
│   │   └── model.safetensors   # ~737 MB — local only / Git LFS
│   └── flan_t5/                # FLAN-T5 question generator
│       ├── config.json
│       ├── generation_config.json
│       ├── spiece.model
│       └── model.safetensors   # ~990 MB — local only / Git LFS
│
├── core/                       # Core question processing engine
│   ├── question_understanding.py   # Domain inference, topic resolution
│   ├── question_profile.py         # Structured question data model
│   ├── candidate_ranker.py         # Multi-candidate scoring & ranking
│   ├── spacy_utils.py              # spaCy NLP helpers & embedding cache
│   ├── prompt_templates.py         # FLAN-T5 instruction prompt builder
│   ├── retry_context.py            # Adaptive retry advisor
│   ├── pipeline_context.py         # Per-request execution state
│   └── domain_hierarchy_builder.py # Domain → subject → topic hierarchy
│
├── validation/                 # 8-stage validation pipeline
│   ├── validation_engine.py    # Orchestrator — runs all 8 stages sequentially
│   ├── bloom_validator.py      # Stage 1
│   ├── concept_validator.py    # Stage 2
│   ├── entity_validator.py     # Stage 3
│   ├── number_validator.py     # Stage 4
│   ├── knowledge_consistency_validator.py  # Stage 5
│   ├── semantic_validator.py   # Stage 6
│   ├── duplicate_validator.py  # Stage 7
│   ├── grammar_validator.py    # Stage 8
│   ├── topic_validator.py      # Topic preservation helper
│   └── validation_models.py    # Output data models (ValidationResult, StageScore)
│
├── knowledge/                  # Static CS knowledge base & ontologies
│   ├── concepts.py             # Concept dictionaries & synonym aliases
│   ├── domains.py              # CS domain definitions (15+ domains)
│   ├── terminology.py          # Technical terminology map
│   ├── hierarchy.py            # Subject–topic hierarchy tree
│   ├── topics.py               # Canonical topic → concept mappings
│   └── generation_context.py   # Topic context for generation prompts
│
├── datasets/
│   ├── classification/
│   │   └── final_dataset_v2.xlsx           # 31,310 records — DeBERTa training data
│   ├── transformation/
│   │   └── combined_cleaned.json           # 21,004 pairs — FLAN-T5 training data
│   └── evaluation/
│       ├── benchmark_dataset.json          # 300-item pipeline benchmark
│       ├── benchmark_dataset_100.json      # 100-item fast benchmark
│       └── manual_review.csv              # Manual QA review records
│
├── notebooks/
│   ├── class.ipynb             # DeBERTa-v3 fine-tuning notebook (Bloom classification)
│   └── FFlan.ipynb             # FLAN-T5 seq2seq fine-tuning notebook
│
├── evaluation/
│   ├── evaluate_pipeline.py    # End-to-end pipeline benchmark script
│   ├── benchmark_understanding.py
│   ├── benchmark_report.md     # Benchmark results & analysis
│   ├── bloomengine_qa_report.md
│   ├── bloomengine_qa_report.html
│   ├── bloomengine_bug_list.csv
│   └── bloomai_production_certificate.md  # Production verification certificate
│
├── tests/
│   ├── test_question_understanding.py
│   ├── test_knowledge_consistency.py
│   ├── test_retry_context.py
│   ├── test_canonical_concepts.py
│   ├── test_fallback_ui.py
│   ├── test_supplements_merged.py
│   ├── test_technical_terminology.py
│   ├── test_debug.py
│   ├── verify_production.py
│   ├── bulk_processing.spec.js
│   ├── exploratory_audit.spec.js
│   ├── batch_processing_regression.spec.js
│   ├── bloom_benchmark.spec.js
│   └── pagination_layout.spec.js
│
├── report/
│   ├── BloomEngine_MCA_Major_Project_Report.docx
│   ├── BloomEngine_MCA_Major_Project_Report.md
│   └── figures/                # All academic diagrams & charts
│
├── templates/                  # HTML UI templates (Jinja2)
├── static/                     # CSS, JS, logo assets
└── archive/                    # Development history & tools archive
```

---

## Installation & Setup

### Prerequisites

- Python 3.12
- Git with Git LFS (for model weights)
- Node.js 18+ (for Playwright E2E tests)

### 1. Clone the repository

```bash
git clone https://github.com/Tharunkumar0910/BloomEngine.git
cd BloomEngine
git lfs pull  # downloads fine-tuned model weights (~1.7 GB)
```

### 2. Create a virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Install spaCy language model

```bash
python -m spacy download en_core_web_sm
```

### 5. Verify model paths

Confirm these files exist after `git lfs pull`:

```
models/classifier/model.safetensors    (~737 MB)
models/flan_t5/model.safetensors       (~990 MB)
```

If you did not use Git LFS, place your locally fine-tuned weights in these directories manually.

---

## Running the Application

```bash
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Server health check |
| `/classify` | POST | Bloom's Taxonomy classification |
| `/rephrase` | POST | Question transformation with 8-stage validation |
| `/export` | POST | Export transformed questions |
| `/batch` | POST | Bulk question processing |

---

## Running Tests

### Python Unit Tests (36 tests)

```bash
pytest tests/ -v
```

### Production Verification

```bash
python tests/verify_production.py
```

### E2E Pipeline Benchmark

```bash
python evaluation/evaluate_pipeline.py
```

### Playwright E2E Tests

```bash
npm install
npx playwright install
npx playwright test
```

---

## Training Details

### DeBERTa-v3 Bloom Classifier

| Parameter | Value |
|-----------|-------|
| Base model | `microsoft/deberta-v3-base` |
| Task | 6-class sequence classification |
| Classes | Remember, Understand, Apply, Analyze, Evaluate, Create |
| Training records | 31,310 |
| Training notebook | `notebooks/class.ipynb` |

### FLAN-T5 Question Generator

| Parameter | Value |
|-----------|-------|
| Base model | `google/flan-t5-base` |
| Task | Seq2Seq instruction-tuned generation |
| Training pairs | 21,004 |
| Generation mode | Multi-candidate beam sampling (Mode E) |
| Training notebook | `notebooks/FFlan.ipynb` |

---

## Generation Configuration (Mode E)

All generation and validation parameters are centralized in [`config.py`](config.py):

```python
# Generation
num_beams              = 8
num_return_sequences   = 3        # candidates per round
max_generation_rounds  = 4
temperature            = 0.7
top_p                  = 0.95

# Validation thresholds
PASS_THRESHOLD                 = 80.0
SEMANTIC_SIMILARITY_FLOOR      = 0.70
DUPLICATE_SEMANTIC_THRESHOLD   = 0.93
CONCEPT_SEMANTIC_THRESHOLD     = 0.75
```

---

## Supported CS Domains

The knowledge base covers **15+ Computer Science domains** including:

- Database Management Systems (ACID, SQL, Normalization, NoSQL)
- Computer Networks (TCP/UDP, OSI, IPv4/IPv6, HTTP/HTTPS)
- Operating Systems (Scheduling, Deadlock, Paging, Semaphores)
- Data Structures & Algorithms
- Machine Learning & Artificial Intelligence
- Software Engineering, Compiler Design, Cloud Computing
- Computer Architecture, Digital Electronics, IoT

---

## License

This project is licensed under the **MIT License**.

---

## Author

**Tharun Kumar** — MCA Major Project  
[GitHub Profile](https://github.com/Tharunkumar0910)

---

## Acknowledgements

- [Hugging Face](https://huggingface.co) — Transformers library, DeBERTa-v3 & FLAN-T5 base models
- [spaCy](https://spacy.io) — Industrial-strength NLP (tokenization, NER, noun chunks)
- [SentenceTransformers](https://www.sbert.net) — Semantic similarity embeddings
- [RapidFuzz](https://github.com/maxbachmann/RapidFuzz) — High-performance fuzzy string matching
- [Playwright](https://playwright.dev) — End-to-end browser testing framework
