# 🛡️ ML Leakage Detector

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12%2B-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Test%20Coverage-70%25-green?logo=shield">
  <img src="https://img.shields.io/badge/License-MIT-yellow?logo=document">
  <img src="https://img.shields.io/badge/Mercor%20Ready-✅-green?logo=check">
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
- **📈 Severity-Based Reporting**: Prioritizes issues by risk level (Critical/High/Medium)
- **🤖 AI-Powered (NEW)**: Auto-generate code fixes with NVIDIA NIM/OpenAI

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

# Sort by severity (Critical first)
ml-leakage-detector examples/ --sort-severity
```

## 📋 Test Results Explained

All **12 tests passed** with production-grade validation:

| Test Name | Purpose | What It Tests |
|-----------|---------|---------------|
| `test_detector_initialization` | Basic Setup | Verifies the detector loads with at least 3 patterns |
| `test_no_leak_in_comments` | Context Awareness | Ensures keywords in comments don't trigger warnings |
| `test_imputation_leak_detection` | Core Pattern | Detects `X.fillna()` or `SimpleImputer()` before splitting |
| `test_scaling_leak_detection` | Core Pattern | Detects `StandardScaler().fit_transform(X)` before splitting |
| `test_sequential_split_detection` | Core Pattern | Detects manual slicing like `X[:800]` instead of `train_test_split` |
| `test_correct_pipeline_no_detection` | False Positive Prevention | Verifies correct usage like `train_test_split()` + `scaler.fit(X_train)` |
| `test_report_generation_with_leakage` | Output Format | Confirms the report lists ALL leaks sorted by severity |
| `test_multiple_leaks_detection` | Comprehensive Scan | Can find 2+ leaks in a single file |
| `test_time_series_shuffle_detection` | Specialized Pattern | Detects `KFold(shuffle=True)` which breaks temporal order |
| `test_target_encoding_detection` | Specialized Pattern | Detects `groupby().mean()` using target variable before split |
| `test_transformer_in_pipeline_not_flagged` | Advanced Logic | **Pipeline Awareness**: Ignores transformers inside `Pipeline([...])` |
| `test_feature_selection_leak_detection` | Specialized Pattern | Detects `SelectKBest().fit(X, y)` before splitting |

## 🎓 For Mercor Interview

This project demonstrates the exact skills tested in Mercor's Domain Expert Assessment:

### The 3 Hardest Interview Questions (And How to Answer)

**Q1: AST Robustness**
> "How would you distinguish between dangerous imputation vs safe imputation AFTER the split?"

- **Answer**: Implement Variable Tracking + Control Flow Analysis
- **Key Phrase**: "Semantic analyzer that understands WHEN operations happen"

**Q2: False Positive Handling**
> "How would you ignore transformers inside sklearn.Pipeline?"

- **Answer**: Use AST node IDs to create a Safe List
- **Key Phrase**: "Production-grade false positive reduction"

**Q3: Production Deployment**
> "How would you prioritize 50 leaks in a legacy codebase?"

- **Answer**: Implement 3-tier severity system (Critical/High/Medium)
- **Key Phrase**: "Turns static analysis into actionable roadmap"

### Interview Talking Points

✅ **Code Validation Skills**: Automated detection of ML bugs using AST  
✅ **Software Engineering**: Clean architecture, 70% test coverage, TDD  
✅ **Production Readiness**: CI/CD integration with exit codes  
✅ **Advanced Logic**: Pipeline awareness and severity-based reporting  

## 🧩 Project Architecture

### The Detective (detector.py)

Uses Python's AST module to traverse code structure:

- **Variable Tracking**: Distinguishes safe vs dangerous operations
- **Pipeline Awareness**: Ignores transformers inside sklearn.Pipeline  
- **Control Flow Analysis**: Understands when splits happen
- **Severity Sorting**: Prioritizes issues by risk level

### The Rulebook (patterns.py)

Defines 6 leakage patterns with severity levels:

- Critical: Target Encoding, Feature Selection, Imputation
- High: Scaling, Time-Series Shuffle
- Medium: Sequential Split

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

🔥 CRITICAL (Fix First)
  • imputation_before_split
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

<p align="center">Built with ❤️ for clean ML pipelines | Mercor Domain Expert Ready 🎯</p>
