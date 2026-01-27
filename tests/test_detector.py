import pytest
from src.detector import LeakageDetector


class TestLeakageDetector:
    @pytest.fixture
    def detector(self):
        return LeakageDetector(verbose=False)

    def test_detector_initialization(self, detector):
        assert detector is not None
        assert len(detector.patterns) >= 3

    def test_imputation_leak_detection(self, detector):
        buggy_code = "X_filled = X.fillna(X.mean())\nX_train = X[:800]"
        result = detector.detect(buggy_code)
        assert result.has_leakage is True
        assert result.leakage_type == "imputation_before_split"

    def test_scaling_leak_detection(self, detector):
        buggy_code = (
            "X_scaled = StandardScaler().fit_transform(X)\nX_train = X_scaled[:800]"
        )
        result = detector.detect(buggy_code)
        assert result.has_leakage is True
        assert "scaling" in result.leakage_type

    def test_sequential_split_detection(self, detector):
        buggy_code = "split_idx = 800\nX_train = X[:split_idx]"
        result = detector.detect(buggy_code)
        assert result.has_leakage is True
        assert result.leakage_type == "sequential_split"

    def test_correct_pipeline_no_detection(self, detector):
        correct_code = "X_train, X_test = train_test_split(X)\nscaler.fit(X_train)"
        result = detector.detect(correct_code)
        assert result.has_leakage is False

    def test_report_generation_with_leakage(self, detector):
        buggy_code = "X.fillna(X.mean())"
        result = detector.detect(buggy_code)
        report = detector.generate_report(result)
        assert "DATA LEAKAGE DETECTED" in report
