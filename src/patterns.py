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
    indicators=[".fillna(", "SimpleImputer(", "KNNImputer("],
    fix_template="Use Pipeline to fit imputer only on training data.",
    severity="Critical",
)

SCALING_BEFORE_SPLIT = LeakagePattern(
    name="scaling_before_split",
    description="Scaling performed on full dataset.",
    indicators=["StandardScaler(", "MinMaxScaler(", "RobustScaler("],
    fix_template="Fit the scaler ONLY on training data.",
    severity="Critical",
)

SEQUENTIAL_SPLIT = LeakagePattern(
    name="sequential_split",
    description="Using sequential slicing instead of random split.",
    indicators=["[:", ":]", ".iloc["],
    fix_template="Use train_test_split with stratification.",
    severity="Medium",
)

ALL_PATTERNS = {
    "imputation": IMPUTATION_BEFORE_SPLIT,
    "scaling": SCALING_BEFORE_SPLIT,
    "sequential_split": SEQUENTIAL_SPLIT,
}
