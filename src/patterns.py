from dataclasses import dataclass
from typing import List


@dataclass
class LeakagePattern:
    name: str
    description: str
    indicators: List[str]
    fix_template: str
    severity: str


IMPUTATION_BEFORE_SPLIT = LeakagePattern(
    name="imputation_before_split",
    description="Imputation performed on full dataset.",
    indicators=["fillna", "SimpleImputer", "KNNImputer"],
    fix_template="Use Pipeline to fit imputer only on training data.",
    severity="Critical",
)

SCALING_BEFORE_SPLIT = LeakagePattern(
    name="scaling_before_split",
    description="Scaling performed on full dataset.",
    indicators=["StandardScaler", "MinMaxScaler", "RobustScaler"],
    fix_template="Fit the scaler ONLY on training data.",
    severity="Critical",
)

SEQUENTIAL_SPLIT = LeakagePattern(
    name="sequential_split",
    description="Using sequential slicing instead of random split.",
    indicators=["slice", "iloc"],
    fix_template="Use train_test_split with stratification.",
    severity="Medium",
)

FEATURE_SELECTION_BEFORE_SPLIT = LeakagePattern(
    name="feature_selection_before_split",
    description="Feature selection (SelectKBest, RFE, etc.) performed on full dataset.",
    indicators=["SelectKBest", "RFE", "RFECV", "SelectFromModel", "VarianceThreshold"],
    fix_template="Perform feature selection only on training data or inside a Pipeline.",
    severity="Critical",
)

TARGET_ENCODING_BEFORE_SPLIT = LeakagePattern(
    name="target_encoding_before_split",
    description="Target encoding performed on full dataset.",
    indicators=["groupby", "map", "TargetEncoder"],
    fix_template="Perform target encoding inside a cross-validation loop or after splitting.",
    severity="Critical",
)

TIME_SERIES_SHUFFLE = LeakagePattern(
    name="time_series_shuffle",
    description="Random shuffling detected which may break temporal dependencies.",
    indicators=["KFold", "ShuffleSplit"],
    fix_template="Use TimeSeriesSplit to maintain temporal order for time-series data.",
    severity="High",
)

ALL_PATTERNS = {
    "imputation": IMPUTATION_BEFORE_SPLIT,
    "scaling": SCALING_BEFORE_SPLIT,
    "sequential_split": SEQUENTIAL_SPLIT,
    "feature_selection": FEATURE_SELECTION_BEFORE_SPLIT,
    "target_encoding": TARGET_ENCODING_BEFORE_SPLIT,
    "time_series_shuffle": TIME_SERIES_SHUFFLE,
}
