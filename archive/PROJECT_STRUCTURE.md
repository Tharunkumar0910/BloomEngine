# Project Structure — BloomAI Arena v2.1

```
BloomAI_Arena_v2_1/
│
├── app.py                          # Flask application entry point. Contains:
│                                   #   - DeBERTa-v3 & FLAN-T5 model loading
│                                   #   - /classify route (single question)
│                                   #   - /generate-bank route (batch generation)
│                                   #   - /generation-status route (polling)
│                                   #   - Background worker (generate_bank_background)
│                                   #   - UNDERSTAND_TEMPLATES / EVALUATE_TEMPLATES rotation pools
│                                   #   - Validation Engine (Exact/Adjacent/Mismatch)
│                                   #   - Diversity Engine (near-duplicate detection)
│                                   #   - Export routes (CSV, Excel, Word, PDF, PPT)
│                                   #   - Review Table edit/delete/restore endpoints
│
├── benchmark.py                    # Standalone Phase 6 benchmark evaluation engine.
│                                   #   Runs independently of FLAN-T5. Loads DeBERTa,
│                                   #   classifies 300 benchmark questions, produces
│                                   #   classification_metrics.json, confusion_matrix.csv,
│                                   #   and misclassified_examples.csv.
│
├── benchmark_dataset.json          # 300 manually curated university-level CS questions.
│                                   #   50 questions per Bloom level × 6 levels.
│                                   #   Covers: DBMS, OS, CN, SE, Cloud, Big Data,
│                                   #   Cyber Security, ML, Data Structures, Compiler Design.
│
├── requirements.txt                # Python dependency list for pip install.
│
├── VERSION.txt                     # Machine-readable version metadata.
├── RELEASE_NOTES.md                # Human-readable feature changelog.
├── PROJECT_STRUCTURE.md            # This file.
│
├── deberta_bloom_model/            # Fine-tuned DeBERTa-v3-small model.
│                                   #   Task: 6-class Bloom taxonomy classification.
│                                   #   Accuracy: 90.33% on 300Q benchmark.
│                                   #   Loaded by: app.py and benchmark.py
│
├── flan_t5_base_bloom_v9/          # Fine-tuned FLAN-T5 Base generation model.
│                                   #   Task: Bloom-aligned academic question generation.
│                                   #   Inference: CPU, temperature=0.8, top_p=0.95.
│                                   #   Loaded by: app.py (Generation Studio)
│
├── templates/
│   └── index.html                  # Single-page Tailwind CSS application shell.
│                                   #   Hosts: Generation Studio, Review Table,
│                                   #   Validation Dashboard, Export panel.
│
├── static/
│   ├── css/
│   │   └── style.css               # Additional custom styles (dark mode, animations,
│   │                               #   layout overrides beyond Tailwind utilities).
│   ├── js/
│   │   └── main.js                 # Core application JavaScript.
│   │                               #   Handles: API calls, Review Table rendering,
│   │                               #   dark mode toggle (.dark class), export triggers,
│   │                               #   Bloom distribution chart, progress polling.
│   └── uploads/                    # Temporary export staging directory.
│                                   #   Generated files are served from here then
│                                   #   auto-cleaned. (Initially empty on fresh deploy.)
│
└── benchmark_results/
    ├── classification_metrics.json # Per-class and macro accuracy/precision/recall/F1.
    ├── confusion_matrix.csv        # 6×6 Expected vs Predicted Bloom level matrix.
    └── misclassified_examples.csv  # All 29 misclassified questions with Error_Type.
```

## Architecture Summary

```
[User Browser]
     │
     ▼
[Flask App — app.py]
     │
     ├──► [DeBERTa-v3] ──► Classification (Bloom Level + Confidence)
     │
     ├──► [FLAN-T5 Base] ──► Question Generation
     │         │
     │         └──► Template Rotation (Understand/Evaluate pools)
     │              Hybrid Prefix Enforcement + Post-gen Correction
     │
     ├──► [Validation Engine] ──► Exact / Adjacent / Mismatch
     │
     ├──► [Diversity Engine] ──► Near-duplicate detection (SequenceMatcher)
     │
     └──► [Export Engine] ──► CSV / Excel / Word / PDF / PPT
```
