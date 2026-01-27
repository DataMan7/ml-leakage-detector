"""
Buggy Pipeline #2: Feature Scaling Before Split

This pipeline demonstrates DATA LEAKAGE by applying StandardScaler
to the entire dataset before splitting.

WHY IT'S WRONG:
StandardScaler calculates mean and std from ALL data. These statistics
include information from the test set, causing leakage.

IMPACT:
- Test accuracy will be artificially high
- Model will fail on truly new data
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

def buggy_scaling_pipeline(df, target_col, feature_cols):
    """
    BUGGY: Scales features before splitting data.
    """
    X = df[feature_cols]
    y = df[target_col]
    
    # ❌ BUG: Scaling happens BEFORE split
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)  # Uses mean/std from ALL data
    X_scaled = pd.DataFrame(X_scaled, columns=feature_cols)
    
    # Split after scaling (too late!)
    split_idx = int(0.8 * len(X_scaled))
    X_train = X_scaled[:split_idx]
    X_test = X_scaled[split_idx:]
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
        'feature1': np.random.randn(100) * 10 + 50,
        'feature2': np.random.randn(100) * 5 + 20,
        'target': np.random.randint(0, 2, 100)
    })
    
    acc, model = buggy_scaling_pipeline(
        sample_df, 
        'target', 
        ['feature1', 'feature2']
    )
    print(f"Accuracy: {acc:.3f} (inflated due to scaling leakage!)")

