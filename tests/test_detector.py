import pytest
from src.detector import LeakageDetector


class TestLeakageDetector:
    @pytest.fixture
    def detector(self):
        return LeakageDetector(verbose=False)

    def test_detector_initialization(self, detector):
        assert detector is not None
        assert len(detector.patterns) >= 3

    def test_no_leak_in_comments(self, detector):
        commented_code = "# This code does NOT use StandardScaler()\nX_train, X_test = train_test_split(X)"
        result = detector.detect(commented_code)
        assert result.has_leakage is False

    def test_imputation_leak_detection(self, detector):
        buggy_code = "X_filled = X.fillna(X.mean())\nX_train = X[:800]"
        result = detector.detect(buggy_code)
        assert result.has_leakage is True
        assert any(leak.name == "imputation_before_split" for leak in result.leaks)

    def test_scaling_leak_detection(self, detector):
        buggy_code = (
            "X_scaled = StandardScaler().fit_transform(X)\nX_train = X_scaled[:800]"
        )
        result = detector.detect(buggy_code)
        assert result.has_leakage is True
        assert any(leak.name == "scaling_before_split" for leak in result.leaks)

    def test_sequential_split_detection(self, detector):
        buggy_code = "split_idx = 800\nX_train = X[:split_idx]"
        result = detector.detect(buggy_code)
        assert result.has_leakage is True
        assert any(leak.name == "sequential_split" for leak in result.leaks)

    def test_correct_pipeline_no_detection(self, detector):
        correct_code = "X_train, X_test = train_test_split(X)\nscaler.fit(X_train)"
        result = detector.detect(correct_code)
        assert result.has_leakage is False

    def test_report_generation_with_leakage(self, detector):
        buggy_code = "X.fillna(X.mean())"
        # Test with multiple leaks to ensure all are reported
        buggy_code = """
X_filled = X.fillna(X.mean())
X_scaled = StandardScaler().fit_transform(X_filled)
"""
        result = detector.detect(buggy_code)
        report = detector.generate_report(result)
        assert "DATA LEAKAGE DETECTED" in report
        assert "imputation_before_split" in report
        assert "scaling_before_split" in report
        assert "CRITICAL" in report

    def test_multiple_leaks_detection(self, detector):
        buggy_code = """
X_filled = X.fillna(X.mean())
X_scaled = StandardScaler().fit_transform(X_filled)
"""
        result = detector.detect(buggy_code)
        assert result.has_leakage is True
        assert len(result.leaks) == 2
        assert any(leak.name == "imputation_before_split" for leak in result.leaks)
        assert any(leak.name == "scaling_before_split" for leak in result.leaks)

    def test_time_series_shuffle_detection(self, detector):
        buggy_code = "cv = KFold(n_splits=5, shuffle=True)\nmodel = cross_val_score(m, X, y, cv=cv)"
        result = detector.detect(buggy_code)
        assert result.has_leakage is True
        assert any(leak.name == "time_series_shuffle" for leak in result.leaks)

    def test_target_encoding_detection(self, detector):
        buggy_code = "encoding = df.groupby('cat')['target'].mean()\ndf['enc'] = df['cat'].map(encoding)"
        result = detector.detect(buggy_code)
        assert result.has_leakage is True
        assert any(leak.name == "target_encoding_before_split" for leak in result.leaks)

    def test_transformer_in_pipeline_not_flagged(self, detector):
        code = """
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.model_selection import KFold

pipe = Pipeline([
    ('imputer', SimpleImputer()),
    ('scaler', StandardScaler())
])

cv = KFold(n_splits=5, shuffle=False) # Should not be flagged
"""
        result = detector.detect(code)
        assert result.has_leakage is False

    def test_feature_selection_leak_detection(self, detector):
        buggy_code = "selector = SelectKBest(k=10).fit(X, y)\nX_new = selector.transform(X)"
        result = detector.detect(buggy_code)
        assert result.has_leakage is True
        assert any(leak.name == "feature_selection_before_split" for leak in result.leaks)
