# Contributing to BloomEngine

Thank you for your interest in contributing to BloomEngine! We welcome contributions from developers, AI engineers, and educators. This guide outlines our workflows and standards.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## Local Development Setup

To set up a local development environment, follow these steps:

1. **Clone the Repository**
   ```bash
   git clone https://github.com/username/bloomengine.git
   cd bloomengine
   ```

2. **Create and Activate a Virtual Environment**
   - **Windows:**
     ```powershell
     python -m venv .venv
     .venv\Scripts\Activate.ps1
     ```
   - **Linux/macOS:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download the spaCy Language Pipeline**
   ```bash
   python -m spacy download en_core_web_sm
   ```

5. **Download Model Weights**
   BloomEngine requires the local weights for DeBERTa-v3 and FLAN-T5. Please download them and place them in the correct directories (see the `README.md` for specific instructions and weights locations).

6. **Run the Application**
   ```bash
   python app.py
   ```

---

## Coding Standards

We follow clean code practices and standard Python styling guidelines:

- **Style Guide:** Adhere to PEP 8 style guidelines.
- **Linting:** We use `flake8` to enforce syntax checks and formatting rules. You can run checks locally via:
  ```bash
  flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
  ```
- **Docstrings & Comments:** All new functions, classes, and methods should contain clear, explanatory docstrings (Google or Sphinx style).

---

## Testing Guidelines

We use Playwright for End-to-End browser UI tests and benchmark suites:

1. **Install Node.js Dependencies**
   ```bash
   npm install
   npx playwright install
   ```

2. **Run Playwright E2E Tests**
   ```bash
   npx playwright test
   ```

3. **Run Performance and Quality Benchmarks**
   ```bash
   python evaluate_pipeline.py
   ```

Please ensure all tests and benchmarks pass successfully before submitting a pull request.

---

## Submitting Pull Requests

1. **Create a Feature Branch:**
   ```bash
   git checkout -b feature/your-awesome-feature
   ```
2. **Commit Your Changes:** Keep commits small, descriptive, and atomic. Follow standard commit messages (e.g., `feat: add custom topic detection`).
3. **Push to Your Fork:**
   ```bash
   git push origin feature/your-awesome-feature
   ```
4. **Submit a Pull Request:** Open a PR against our `main` branch. Provide a clear description of the changes using the Pull Request template.
