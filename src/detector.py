import ast
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from .patterns import ALL_PATTERNS, LeakagePattern


@dataclass
class DetectionResult:
    has_leakage: bool
    leakage_type: Optional[str] = None
    confidence: float = 0.0
    fix_suggestion: str = ""
    details: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class LeakageDetector:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.patterns = ALL_PATTERNS

    def detect(self, code: str) -> DetectionResult:
        # Remove all whitespace to make pattern matching easier for slicing [: ]
        collapsed_code = "".join(code.split())

        for key in self.patterns:
            pattern = self.patterns[key]
            for indicator in pattern.indicators:
                # Remove spaces from indicator too for matching
                collapsed_indicator = "".join(indicator.split())
                if collapsed_indicator in collapsed_code:
                    return DetectionResult(
                        has_leakage=True,
                        leakage_type=pattern.name,
                        confidence=0.9,
                        fix_suggestion=pattern.fix_template,
                        details={"severity": pattern.severity},
                    )

        return DetectionResult(
            has_leakage=False, confidence=0.95, fix_suggestion="Pipeline appears clean."
        )

    def generate_report(self, result: DetectionResult) -> str:
        if not result.has_leakage:
            return "✅ No data leakage detected. Pipeline appears clean."
        return f"🚨 DATA LEAKAGE DETECTED\nType: {result.leakage_type}\nFix: {result.fix_suggestion}"
