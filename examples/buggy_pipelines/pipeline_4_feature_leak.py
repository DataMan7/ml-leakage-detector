"""
Buggy Pipeline #4: Feature Engineering with Test Statistics

This pipeline demonstrates DATA LEAKAGE by creating features using
statistics calculated from the entire dataset.

WHY IT'S WRONG:
Creating features like "above_average" using global mean includes
information from test data in the feature engineering process.

IMPACT:
- Model learns patterns that won't exist in production
- Overestimated performance
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

def buggy_feature_engineering_pipeline(df, target_col, feature_cols):
    """
    BUGGY: Creates features using global statistics.
    """
    X = df[feature_cols].copy()
    y = df[target_col]
    
    # ❌ BUG: Calculate mean from ALL data
    global_mean = X['feature1'].mean()
    global_median = X['feature1'].median()
    
    # Create features using these leaked statistics
    X['above_mean'] = (X['feature1'] > global_mean).astype(int)
    X['above_median'] = (X['feature1'] > global_median).astype(int)
    
    # Split AFTER feature engineering (too late!)
    split_idx = int(0.8 * len(X))
    X_train = X[:split_idx]
    X_test = X[split_idx:]
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
    
    sample_df = pd.DataFrame({
        'feature1': np.random.randn(150) * 10,
        'feature2': np.random.randn(150) * 5,
        'target': np.random.randint(0, 2, 150)
    })
    
    acc, model = buggy_feature_engineering_pipeline(
        sample_df, 
        'target',
        ['feature1', 'feature2']
    )
    print(f"Accuracy: {acc:.3f} (leakage from global statistics!)")
