# 🎯 ML Leakage Detector - Kaggle Integration Guide

*A complete guide for Kaggle users to validate their competition notebooks*

---

## 🤔 Why Kaggle Users Need This

**The Problem:**

- 60% of Kaggle solutions have data leakage
- Leaderboard looks great → Real world fails
- You don't know until production deployment

**Our Solution:**

- Scan your notebook before submission
- Find leakage patterns that inflate your score
- Fix issues before they hurt you

---

## 📊 Real Example: Tested on Intelligent Retail Analytics

We tested the detector on a real Kaggle-style project and found **37 leaks**:

```bash
$ ml-leakage-detector /path/to/project/

📊 SUMMARY: 37 leaks found
  🔴 Critical: 5    ← Target encoding + Scaling
  🟠 High: 0
  🟡 Medium: 32     ← Sequential splits
```

### Critical Issues Found in `churn_prediction_template.py`

```
🔥 CRITICAL (Fix First)
  • target_encoding_before_split (3 times!)
  • scaling_before_split (2 times!)
```

This is exactly the kind of issue that inflates leaderboard scores but fails in production!

---

## 🚀 Quick Start for Kaggle Users

### Option 1: In Your Local Environment

```bash
# Install
pip install ml-leakage-detector

# Clone your Kaggle notebook code locally
git clone your-kaggle-notebook-repo
cd your-project

# Scan for leaks
ml-leakage-detector .
```

### Option 2: Direct in Kaggle Notebook

```python
# In a Kaggle notebook cell
!pip install ml-leakage-detector -q

from src.detector import LeakageDetector

# Paste your preprocessing code here
my_code = """
df = pd.read_csv('data.csv')
X = df.drop('target', axis=1)
y = df['target']

# This is leakage!
X = X.fillna(X.mean())  # Using full data mean
"""

detector = LeakageDetector()
result = detector.detect(my_code)

if result.has_leakage:
    print("⚠️ LEAKAGE DETECTED!")
    print(detector.generate_report(result))
else:
    print("✅ No leakage - safe to submit!")
```

### Option 3: Upload to Kaggle as Dataset

1. Run detector on your local code
2. Export results to JSON: `ml-leakage-detector . --json > results.json`
3. Include results in your Kaggle dataset documentation

---

## 🔍 How to Use Before Each Submission

### Pre-Submission Checklist

```bash
# 1. Scan your entire project
ml-leakage-detector . --json > scan_results.json

# 2. Check for CRITICAL issues
grep -i "critical" scan_results.json

# 3. If any Critical issues found:
#    - DO NOT SUBMIT until fixed
#    - Fix the issues
#    - Rescan

# 4. If only Medium issues:
#    - Review them
#    - Decide if safe to submit
```

---

## 💡 Common Kaggle Leakage Patterns We Detect

### 1. Target Encoding Leak (Critical)

```python
# ❌ LEAKAGE - Using target to create features before split
df['mean_target'] = df.groupby('category')['target'].transform('mean')

# ✅ SAFE - Inside CV loop
for train_idx, val_idx in kf.split(df):
    df.loc[val_idx, 'mean_target'] = df.loc[train_idx].groupby('category')['target'].mean()
```

### 2. Scaling Leak (Critical)

```python
# ❌ LEAKAGE - Scaling full data
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)  # Uses test set stats!

# ✅ SAFE - Only on training data
X_train, X_test = train_test_split(X)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
```

### 3. Imputation Leak (Critical)

```python
# ❌ LEAKAGE - Impute before split
X = X.fillna(X.mean())  # Uses test set values!

# ✅ SAFE - In pipeline or after split
from sklearn.impute import SimpleImputer
pipe = Pipeline([('imputer', SimpleImputer()), ...])
pipe.fit(X_train)
```

### 4. Sequential Split (Medium - Often OK in Time Series)

```python
# ⚠️ MEDIUM - May cause issues
X_train = X[:800]  # Not random!

# ✅ BEST - Random split
X_train, X_test = train_test_split(X, test_size=0.2)
```

### 5. Feature Selection Leak (Critical)

```python
# ❌ LEAKAGE - Selecting features with full data
selector = SelectKBest(k=10)
selector.fit(X, y)  # Uses test labels!
X_new = selector.transform(X)

# ✅ SAFE - Inside CV or Pipeline
pipe = Pipeline([('selector', SelectKBest(k=10)), ...])
```

---

## 🎯 Use Cases for Different Kaggle Competitions

| Competition Type | What to Watch | Priority |
|----------------|---------------|----------|
| **Tabular** | Target encoding, scaling, imputation | 🔴 Critical |
| **NLP** | Text preprocessing before split | 🟠 High |
| **Time Series** | Shuffling, look-ahead bias | 🔴 Critical |
| **Image/Video** | Test-time augmentation | 🟡 Medium |
| **Recommender** | User-item stats on full data | 🔴 Critical |

---

## 🛠️ Integration with Kaggle Workflow

### GitHub + Kaggle

```bash
# 1. Link your Kaggle to GitHub
# Kaggle → Account → Linked accounts

# 2. Run detector before pushing
ml-leakage-detector . --json

# 3. If clean, push to GitHub
git add .
git commit -m "Valid submission - no leakage"
git push origin main

# 4. Kaggle pulls from GitHub automatically
```

### CI/CD for Kaggle

Create a GitHub Action that runs detector before merge:

```yaml
# .github/workflows/kaggle-check.yml
name: Leakage Check
on: [pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install ml-leakage-detector
      - run: ml-leakage-detector . --json
        # Fails if Critical leaks found
```

---

## 📈 Example: Before & After Fix

### Before (Has Leakage)

```python
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

df = pd.read_csv('data.csv')
X = df.drop('target', axis=1)
y = df['target']

# ❌ LEAKAGE: Using full data for scaling
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ❌ LEAKAGE: Using sequential split
X_train = X_scaled[:800]
X_test = X_scaled[800:]
y_train = y[:800]
y_test = y[800:]
```

### After (Fixed)

```python
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

df = pd.read_csv('data.csv')
X = df.drop('target', axis=1)
y = df['target']

# ✅ CORRECT: Split first, then scale
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ✅ CORRECT: Fit only on training data
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
```

---

## 💰 How to Monetize for Kaggle Users

| Product | Price | Kaggle User Value |
|---------|-------|-------------------|
| **Free** | $0 | Basic CLI, 6 patterns |
| **Pro** | $19/mo | AI auto-fix, priority support |
| **Team** | $49/mo | Team dashboard, Slack integration |
| **Consulting** | $500/project | I'll scan your notebook for you |

---

## 🎓 Training Material Included

Show users they can learn from the tool:

1. **Examples folder** - Shows all 6 leak types with code
2. **Documentation** - Explains WHY each pattern is dangerous
3. **AI explanations** - Tells users how to fix each issue

---

## 📝 Quick Commands Reference

```bash
# Basic scan
ml-leakage-detector /path/to/code

# JSON output (for automation)
ml-leakage-detector /path/to/code --json

# AI-powered fixes
ml-leakage-detector /path/to/code --ai-fix

# Sort by severity
ml-leakage-detector /path/to/code --sort-severity
```

---

*Built for Kaggle Grandmasters by Dennis Omboga* 🏆
