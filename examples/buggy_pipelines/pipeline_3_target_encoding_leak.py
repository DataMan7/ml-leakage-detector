"""
Buggy Pipeline #3: Target Encoding Before Split

This pipeline demonstrates DATA LEAKAGE by performing target encoding
(mean encoding) on the full dataset before splitting.

WHY IT'S WRONG:
Target encoding uses the TARGET variable to create features. If done
on the full dataset, test set targets are used to encode train data.

IMPACT:
- Severe leakage: model sees future information
- Unrealistic performance estimates
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

def buggy_target_encoding_pipeline(df, target_col, categorical_col, feature_cols):
    """
    BUGGY: Performs target encoding before splitting.
    """
    X = df[feature_cols + [categorical_col]].copy()
    y = df[target_col]
    
    # ❌ BUG: Target encoding uses ALL data including test targets
    encoding_map = df.groupby(categorical_col)[target_col].mean().to_dict()
    X['category_encoded'] = X[categorical_col].map(encoding_map)
    X = X.drop(columns=[categorical_col])
    
    # Split AFTER encoding (too late!)
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
        'feature1': np.random.randn(200),
        'category': np.random.choice(['A', 'B', 'C'], 200),
        'target': np.random.randint(0, 2, 200)
    })
    
    acc, model = buggy_target_encoding_pipeline(
        sample_df, 
        'target',
        'category',
        ['feature1']
    )
    print(f"Accuracy: {acc:.3f} (severe leakage from target encoding!)")
