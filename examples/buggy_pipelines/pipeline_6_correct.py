"""
Correct Pipeline: No Data Leakage

This pipeline demonstrates the CORRECT approach to building an ML pipeline
without data leakage.

KEY PRINCIPLES:
1. Split data FIRST (random, stratified)
2. Use Pipeline to encapsulate preprocessing
3. Fit preprocessing ONLY on training data
4. Transform test data using training statistics
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report

def correct_pipeline(df, target_col, feature_cols, test_size=0.2, random_state=42):
    """
    CORRECT: Proper ML pipeline with no data leakage.
    """
    X = df[feature_cols].copy()
    y = df[target_col].copy()
    
    # ✅ STEP 1: Split FIRST with random shuffling and stratification
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=test_size,
        random_state=random_state,
        stratify=y  # Preserves class distribution
    )
    
    # ✅ STEP 2: Build Pipeline (ensures no leakage)
    pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),  # Fits on train only
        ('scaler', StandardScaler()),                    # Fits on train only
        ('classifier', LogisticRegression(
            random_state=random_state,
            max_iter=1000,
            class_weight='balanced'
        ))
    ])
    
    # ✅ STEP 3: Train (imputer and scaler fit only on X_train)
    pipeline.fit(X_train, y_train)
    
    # ✅ STEP 4: Evaluate (transforms test using train statistics)
    y_pred = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print("✅ CORRECT PIPELINE RESULTS")
    print(f"Accuracy: {accuracy:.3f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    return accuracy, pipeline


if __name__ == "__main__":
    np.random.seed(42)
    
    # Create sample data with missing values and imbalance
    sample_df = pd.DataFrame({
        'feature1': [np.nan if i % 7 == 0 else np.random.randn() * 10 
                     for i in range(200)],
        'feature2': np.random.randn(200) * 5,
        'target': np.random.choice([0, 1], 200, p=[0.7, 0.3])  # Imbalanced
    })
    
    acc, pipeline = correct_pipeline(
        sample_df, 
        'target',
        ['feature1', 'feature2']
    )
    
    print("\n✅ This pipeline is clean. It can be used in production.")
