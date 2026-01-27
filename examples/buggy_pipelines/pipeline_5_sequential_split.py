"""
Buggy Pipeline #5: Sequential Split (Temporal Leakage)

This pipeline demonstrates BIAS by using sequential slicing instead
of random splitting for non-temporal data.

WHY IT'S WRONG:
Using [:800] and [800:] assumes data has no inherent order. If data
is sorted by any feature correlated with target, this introduces bias.

IMPACT:
- Biased performance estimates
- Model fails on truly random data
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

def buggy_sequential_split_pipeline(df, target_col, feature_cols):
    """
    BUGGY: Uses sequential split instead of random split.
    """
    X = df[feature_cols]
    y = df[target_col]
    
    # ❌ BUG: Sequential split instead of random
    # This assumes data is randomly ordered (often not true!)
    split_idx = int(0.8 * len(X))
    X_train = X[:split_idx]  # First 80%
    X_test = X[split_idx:]   # Last 20%
    y_train = y[:split_idx]
    y_test = y[split_idx:]
    
    # Train model
    model = LogisticRegression()
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    return accuracy, model


if __name__ == "__main__":
    np.random.seed(42)
    
    # Create SORTED data to demonstrate the problem
    sample_df = pd.DataFrame({
        'feature1': np.linspace(0, 100, 100),  # Sorted!
        'feature2': np.random.randn(100),
        'target': (np.linspace(0, 100, 100) > 50).astype(int)  # Correlated with feature1
    })
    
    acc, model = buggy_sequential_split_pipeline(
        sample_df, 
        'target',
        ['feature1', 'feature2']
    )
    print(f"Accuracy: {acc:.3f} (biased due to sequential split!)")
