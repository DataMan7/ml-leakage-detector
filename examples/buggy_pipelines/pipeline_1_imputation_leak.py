"""
Buggy Pipeline #1: Imputation Before Split

This pipeline demonstrates DATA LEAKAGE by performing mean imputation
on the entire dataset before splitting into train/test sets.

WHY IT'S WRONG:
The mean is calculated from ALL data (including test data), which means
information from the test set is "leaking" into the training process.

IMPACT:
- Model performance will be artificially inflated
- Model won't generalize well to truly unseen data
"""

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

def buggy_train_pipeline(df, target_col, feature_cols):
    """
    BUGGY: Imputes missing values before splitting data.
    """
    # Separate features and target
    X = df[feature_cols]
    y = df[target_col]
    
    # ❌ BUG: Imputation happens BEFORE split
    # This calculates mean from the ENTIRE dataset, including test data
    X_filled = X.fillna(X.mean())
    
    # Now split the data
    split_idx = int(0.8 * len(X_filled))
    X_train = X_filled[:split_idx]
    X_test = X_filled[split_idx:]
    y_train = y[:split_idx]
    y_test = y[split_idx:]
    
    # Train model
    model = LogisticRegression()
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    return accuracy, model


# Example usage (for testing)
if __name__ == "__main__":
    # Create sample data with missing values
    import numpy as np
    np.random.seed(42)
    
    sample_df = pd.DataFrame({
        'feature1': [1, 2, np.nan, 4, 5, 6, 7, 8, 9, 10],
        'feature2': [10, 9, 8, 7, np.nan, 5, 4, 3, 2, 1],
        'target': [0, 0, 1, 1, 0, 1, 0, 1, 0, 1]
    })
    
    acc, model = buggy_train_pipeline(
        sample_df, 
        'target', 
        ['feature1', 'feature2']
    )
    print(f"Accuracy: {acc:.3f} (but this is misleading due to leakage!)")
