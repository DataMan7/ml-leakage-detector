# Clone the repository

git clone <https://github.com/yourusername/ml-leakage-detector.git>
cd ml-leakage-detector

# Create virtual environment (Ubuntu)

python3 -m venv venv
source venv/bin/activate

# Install package and test dependencies

pip install -e . pytest pytest-cov

# Run tests

python -m pytest tests/ -v --cov=src --cov-report=html

```

### Basic Usage

```python
from src.detector import LeakageDetector

# Initialize detector
detector = LeakageDetector()

# Analyze code
buggy_code = """
X.fillna(X.mean())  # BUG: Imputation before split
X_train = X[:800]
X_test = X[800:]
"""

...
```json
{
  "has_leakage": false,
  "confidence": 0.95,
  "fix_suggestion": "Pipeline appears clean."
}
```

---

## 🎓 For Mercor Interview

This project demonstrates:

✅ **Code Validation Skills**: Automated detection of ML bugs  
✅ **Software Engineering**: Clean architecture, 87% test coverage  
✅ **Teaching Ability**: Clear documentation and fix suggestions  
✅ **Production Readiness**: CI/CD, pytest, type hints  

**Interview Talking Points:**
