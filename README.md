# 🛡️ ML Leakage Detector

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12%2B-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Test%20Coverage-70%25-green?logo=shield">
  <img src="https://img.shields.io/badge/License-MIT-yellow?logo=document">
  <img src="https://img.shields.io/badge/Mercor%20Ready-✅-green?logo=check">
  <img src="https://img.shields.io/badge/AI%20Powered-🤖-purple?logo=rocket">
</p>

**ML Leakage Detector** is a production-grade static analysis tool that detects data leakage patterns in Machine Learning pipelines. It uses Python's Abstract Syntax Tree (AST) for intelligent code analysis and is now enhanced with **NVIDIA NIM AI** for automatic code fixes!

## 🎯 What is Data Leakage?

In ML, **Data Leakage** occurs when information from the test set "leaks" into the training process. This makes the model look accurate during development but fail in the real world—similar to a student seeing the answers before the exam.

> **Simple Analogy:** It's like a teacher giving students the exam answers BEFORE the test. They look perfect in class, but fail in the real world!

## ✨ Features

### Core Features (Free)

- **🔍 AST-Based Detection**: Uses Python's Abstract Syntax Tree to understand code logic
- **🤖 Pipeline Awareness**: Intelligently ignores transformers inside `sklearn.Pipeline`
- **📊 6 Pattern Types**:
  - Imputation before split
  - Scaling before split
  - Target encoding before split
  - Feature selection before split
  - Sequential split (no shuffling)
  - Time-series shuffle
- **🔄 CLI Support**: Scan directories with JSON output for CI/CD
- **✅ 12 Passing Tests**: 70% code coverage

### AI Features (NEW!)

- **🤖 AI Code Doctor**: Auto-generates corrected code using NVIDIA NIM
- **💬 NLP Auditor**: Describe issues in plain English, get AI analysis
- **🧠 Smart Context Analyzer**: Reduces false positives with AI
- **🔍 Pattern Discovery Engine**: AI finds NEW leakage patterns

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/DataMan7/ml-leakage-detector.git
cd ml-leakage-detector

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install package and dependencies
pip install -e . 

# Copy and configure environment
cp .env.example .env
# Add your NVIDIA_API_KEY (get free at https://org.ngc.nvidia.com/)
```

### Running Tests

```bash
# Run all tests
python3 -m pytest tests/ -v

# Run with coverage
python3 -m pytest tests/ -v --cov=src --cov-report=html
```

### Using the CLI

```bash
# Basic scan
ml-leakage-detector examples/

# AI-powered fix
ml-leakage-detector examples/ --ai-fix

# JSON output (for CI/CD)
ml-leakage-detector examples/ --json

# NLP audit (describe in English)
ml-leakage-detector --nlp "I fill missing values with the mean of my whole dataset"
```

## 📓 Kaggle Integration

We've tested the detector on real Kaggle projects and found **37 leaks** in typical competition code!

### Quick Start for Kaggle Users

```python
# In a Kaggle notebook
!pip install ml-leakage-detector -q

from src.detector import LeakageDetector

detector = LeakageDetector()
result = detector.detect(your_preprocessing_code)

if result.has_leakage:
    print("⚠️ LEAKAGE DETECTED - Do not submit!")
else:
    print("✅ Safe to submit!")
```

See [`docs/KAGGLE_INTEGRATION.md`](docs/KAGGLE_INTEGRATION.md) for complete guide with examples from real Kaggle projects.

## 📊 Detected Leakage Patterns

| Pattern | Severity | Description |
|---------|----------|-------------|
| Imputation | 🔴 Critical | `fillna()` or `SimpleImputer` before split |
| Scaling | 🔴 Critical | `StandardScaler().fit_transform(X)` before split |
| Target Encoding | 🔴 Critical | `groupby().mean()` using target before split |
| Feature Selection | 🔴 Critical | `SelectKBest().fit(X, y)` before split |
| Time Series Shuffle | 🟠 High | `KFold(shuffle=True)` for time-series data |
| Sequential Split | 🟡 Medium | Manual slicing `X[:800]` instead of random split |

## 🤖 AI Features (NVIDIA NIM)

### Setting Up AI

```bash
# Get your free NVIDIA API key at:
# https://org.ngc.nvidia.com/

# Add to .env file
NVIDIA_API_KEY=your_key_here
```

### AI Code Doctor Example

**Input (Buggy):**

```python
X_filled = X.fillna(X.mean())  # Leakage!
X_train = X_filled[:800]
```

**AI Output:**

```python
# FIXED CODE:
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split

X_train, X_test = train_test_split(X, test_size=0.2)

pipeline = Pipeline([
    ('imputer', SimpleImputer())
])

X_train_filled = pipeline.fit_transform(X_train)
X_test_filled = pipeline.transform(X_test)
```

## 🏗️ Project Architecture

```
ml-leakage-detector/
├── src/
│   ├── detector.py         # Core AST-based detection engine
│   ├── patterns.py         # Leakage pattern definitions
│   └── ai_detector.py     # AI-powered features (NVIDIA NIM)
├── tests/
│   └── test_detector.py   # 12 comprehensive tests
├── examples/
│   ├── demo.py             # Usage examples
│   └── buggy_pipelines/   # Example leaky code
├── .github/
│   └── workflows/         # CI/CD automation
├── docs/
│   ├── DEPLOYMENT_GUIDE.md      # AWS EC2 + Docker
│   ├── AI_ARCHITECTURE.md       # AI features spec
│   ├── MONETIZATION_PLAN.md     # Business strategy
│   └── NON_TECHNICAL_GUIDE.md  # For non-technical users
└── README.md
```

## 📋 Test Results

```
======================== 12 passed in 0.06s ========================

Tests:
✅ test_detector_initialization
✅ test_no_leak_in_comments
✅ test_imputation_leak_detection
✅ test_scaling_leak_detection
✅ test_sequential_split_detection
✅ test_correct_pipeline_no_detection
✅ test_report_generation_with_leakage
✅ test_multiple_leaks_detection
✅ test_time_series_shuffle_detection
✅ test_target_encoding_detection
✅ test_transformer_in_pipeline_not_flagged
✅ test_feature_selection_leak_detection
```

## 🎓 For Mercor Interview

This project demonstrates:

### Technical Skills

- ✅ AST-based code analysis (not just regex)
- ✅ Production-grade error handling
- ✅ CI/CD integration (GitHub Actions)
- ✅ AI integration (NVIDIA NIM)

### Engineering Skills

- ✅ Test-driven development (12 tests)
- ✅ Clean architecture
- ✅ Documentation for multiple audiences
- ✅ API design

## 💰 Monetization Ready

| Tier | Price | Features |
|------|-------|----------|
| **Free** | $0 | Basic detection, CLI |
| **Pro** | $19/mo | AI Code Doctor, NLP Audit |
| **Team** | $49/mo | Team dashboard, Slack alerts |
| **Enterprise** | $199/mo | Custom rules, on-prem |

See `MONETIZATION_PLAN.md` for full business strategy.

## 📖 More Documentation

All documentation is in the `docs/` folder:

| Document | Who It's For |
|----------|--------------|
| `README.md` | Everyone - overview |
| `docs/NON_TECHNICAL_GUIDE.md` | Non-technical stakeholders |
| `docs/DEPLOYMENT_GUIDE.md` | DevOps & engineers |
| `docs/AI_ARCHITECTURE.md` | AI/ML engineers |
| `docs/MONETIZATION_PLAN.md` | Business stakeholders |

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

MIT License - See LICENSE file for details.

## 👨‍💻 Author

**Dennis Omboga** - Data & AI Engineer, Founder of Watoto na Codi

- GitHub: [@DataMan7](https://github.com/DataMan7)
- LinkedIn: [dennis-mongare](https://linkedin.com/in/dennis-mongare)
- Platform: [watotonacodi.com](https://watotonacodi.com)

---

<p align="center">Built with ❤️ for clean ML pipelines | Mercor Domain Expert Ready 🎯 | AI Powered 🤖</p>
