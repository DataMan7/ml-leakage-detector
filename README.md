# 🛡️ ML Leakage Detector

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12%2B-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Test%20Coverage-70%25-green?logo=shield">
  <img src="https://img.shields.io/badge/License-MIT-yellow?logo=document">
</p>

**ML Leakage Detector** is a production-grade static analysis tool that detects data leakage patterns in Machine Learning pipelines using Python's Abstract Syntax Tree (AST). It helps data scientists and ML engineers identify and fix common mistakes that lead to overly optimistic model performance.

## 🎯 What is Data Leakage?

In ML, **Data Leakage** occurs when information from the test set "leaks" into the training process. This makes the model look accurate during development but fail in the real world—similar to a student seeing the answers before the exam.

## ✨ Features

- **🔍 AST-Based Detection**: Uses Python's Abstract Syntax Tree to understand code logic, not just keywords
- **🤖 Pipeline Awareness**: Intelligently ignores transformers correctly placed inside `sklearn.Pipeline`
- **📊 Multi-Pattern Support**: Detects 6 critical leakage types:
  - Imputation before split
  - Scaling before split
  - Target encoding before split
  - Feature selection before split
  - Sequential split (no shuffling)
  - Time-series shuffle
- **🔄 CLI Support**: Scan entire directories with JSON output for CI/CD integration
- **✅ Test Coverage**: 70% coverage with 12 passing tests

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/DataMan7/ml-leakage-detector.git
cd ml-leakage-detector

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install package and test dependencies
pip install -e . pytest pytest-cov
```

### Running Tests

```bash
# Run all tests with coverage report
python -m pytest tests/ -v --cov=src --cov-report=html

# Run tests without coverage (faster)
python -m pytest tests/ -v

# Run a specific test
python -m pytest tests/test_detector.py::TestLeakageDetector::test_imputation_leak_detection -v
```

### Using the CLI

```bash
# Scan a single file
ml-leakage-detector examples/buggy_pipelines/pipeline_1_imputation_leak.py

# Scan a directory
ml-leakage-detector examples/

# Output as JSON (for CI/CD)
ml-leakage-detector examples/ --json
```

## 📋 Test Results Explained

The test suite validates that the detector correctly identifies leakage patterns while avoiding false positives. Here's what each test validates:

| Test Name | Purpose | What It Tests |
|-----------|---------|---------------|
| `test_detector_initialization` | Basic Setup | Verifies the detector loads with at least 3 patterns |
| `test_no_leak_in_comments` | Context Awareness | Ensures keywords in comments (e.g., `# StandardScaler`) don't trigger warnings |
| `test_imputation_leak_detection` | Core Pattern | Detects `X.fillna()` or `SimpleImputer()` before splitting |
| `test_scaling_leak_detection` | Core Pattern | Detects `StandardScaler().fit_transform(X)` before splitting |
| `test_sequential_split_detection` | Core Pattern | Detects manual slicing like `X[:800]` instead of `train_test_split` |
| `test_correct_pipeline_no_detection` | False Positive Prevention | Verifies correct usage like `train_test_split()` + `scaler.fit(X_train)` |
| `test_report_generation_with_leakage` | Output Format | Confirms the report lists ALL leaks found, not just the first one |
| `test_multiple_leaks_detection` | Comprehensive Scan | Can find 2+ leaks in a single file (e.g., both imputation AND scaling) |
| `test_time_series_shuffle_detection` | Specialized Pattern | Detects `KFold(shuffle=True)` which breaks temporal order |
| `test_target_encoding_detection` | Specialized Pattern | Detects `groupby().mean()` using target variable before split |
| `test_transformer_in_pipeline_not_flagged` | Advanced Logic | **Pipeline Awareness**: Ignores transformers inside `Pipeline([...])` |
| `test_feature_selection_leak_detection` | Specialized Pattern | Detects `SelectKBest().fit(X, y)` before splitting |

### Current Test Status

```
======================== 12 passed in 0.31s ========================
Coverage: src/detector.py (66%), src/patterns.py (100%)
```

## 🧩 Project Architecture

### Non-Technical Guide (For Interviews)

**The Big Picture**: Imagine you're a teacher trying to prevent students from cheating on an exam. Our tool acts as an **Automated Proctor** that reviews the teacher's lesson plan (code) to ensure the answer key is hidden properly.

### Folder & File Breakdown

| Directory/File | Description |
|---------------|-------------|
| `src/detector.py` | **The Detective**: Uses AST parsing to traverse code logic. It distinguishes between "bad words" in comments vs actual dangerous code execution. |
| `src/patterns.py` | **The Rulebook**: Defines what constitutes "cheating" (e.g., calculating mean of entire dataset before split). |
| `tests/` | **The Quality Check**: Automated exams for the detector. We give it tricky code to prove it's reliable. |
| `examples/buggy_pipelines/` | **Scary Stories**: Real-world examples of code that looks okay but leaks data. |
| `.github/workflows/` | **The Security Guard**: CI/CD automation that blocks leaky code from being merged. |

### How It All Connects

1. You run `ml-leakage-detector` on your project
2. The **Detective** reads your Python files
3. It converts code into an AST (a logical tree structure)
4. It walks through the tree using the **Rulebook** patterns
5. If it finds a match, it generates a Report with the leak type and fix suggestion
6. The **Security Guard** (GitHub Action) blocks any merge that contains leakage

## 📖 Example Usage

```python
from src.detector import LeakageDetector

detector = LeakageDetector()

# Example of detected leakage
buggy_code = """
X_filled = X.fillna(X.mean())  # Leakage: imputation on full data
X_train = X_filled[:800]
"""

result = detector.detect(buggy_code)
print(detector.generate_report(result))
```

**Output:**

```
🚨 DATA LEAKAGE DETECTED
--- Leak 1 ---
Type: imputation_before_split (Severity: Critical)
Description: Imputation performed on full dataset.
Fix: Use Pipeline to fit imputer only on training data.
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

MIT License - see LICENSE file for details.

## 👨‍💻 Author

**Dennis Omboga** - Data & AI Engineer, Founder of Watoto na Codi

- GitHub: [@DataMan7](https://github.com/DataMan7)
- LinkedIn: [dennis-mongare](https://linkedin.com/in/dennis-mongare)
- Portfolio: [watotonacodi.com](https://watotonacodi.com)

---

<p align="center">Built with ❤️ for clean ML pipelines</p>
