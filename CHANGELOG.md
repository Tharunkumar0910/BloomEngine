# Changelog

All notable changes to the BloomEngine project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2026-07-13

### Added
- **7-Stage Modular NLP Validation Pipeline**: Replaced legacy heuristic checks with modular validators:
  - *Bloom Verb Constraints* (taxonomy validation)
  - *Concept Preservation* (spaCy noun chunk matching)
  - *Entity Validation* (NER & jargon tracking)
  - *Number Preservation* (digit and version validators)
  - *Semantic Similarity* (sentence embeddings matching)
  - *Duplicate Detection* (recent prompt similarity filter)
  - *Grammar Check* (phrase structure and repetitions)
- **Production Verification Suite (`verify_production.py`)**: Sequential loading check, zero meta-tensors assertion, warmup logging, and pipeline E2E testing.
- **Node.js Playwright Integration**: Real-time browser benchmarking and bulk processing spec automation.
- **Segmented Header Theme Control**: Premium toggle for Light/Dark modes in the UI with instant color updates.
- **Open Source Community Templates**: LICENSE, CONTRIBUTING guidelines, issue templates, security policy, and code of conduct.

### Changed
- **UI Navigation Refinement**: Cleaned up the sidebar by removing legacy badges and online-status indicators to optimize screen space.
- **Fallback Configurations**: Enhanced `app.py` secret key loading with secure environment variable checks.
- **Model Storage Strategy**: Excluded heavy model weights (`*.safetensors`) from version control to maintain a lightweight repository structure while retaining core config files.

### Removed
- **Unused Build Artifacts**: Deleted redundant `app_backup.py` and intermediate checkpoint folders saving over 6 GB of repository space.

---

*Note: For older version histories, please consult the project archives.*
