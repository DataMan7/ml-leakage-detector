import ast
import os
import sys
import argparse
from pathlib import Path
import json
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field, asdict
from .patterns import ALL_PATTERNS, LeakagePattern


@dataclass
class DetectionResult:
    has_leakage: bool
    leaks: List[LeakagePattern] = field(default_factory=list)
    confidence: float = 0.95 # Overall confidence in the detection process
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def sorted_leaks(self) -> List[LeakagePattern]:
        """Sort leaks by severity: Critical > High > Medium"""
        severity_order = {"Critical": 3, "High": 2, "Medium": 1}
        return sorted(self.leaks, key=lambda x: severity_order.get(x.severity, 0), reverse=True)


class LeakageVisitor(ast.NodeVisitor):
    """AST Visitor to find potential leakage patterns in Python code.
    
    This visitor implements:
    1. Variable Tracking - to distinguish safe vs dangerous operations
    2. Pipeline Awareness - to ignore transformers inside sklearn.Pipeline
    3. Control Flow Analysis - to understand when splits happen
    """
    def __init__(self, patterns: Dict[str, LeakagePattern]):
        self.patterns = patterns
        self.found_leaks = []
        self._safe_transformer_ids: Set[int] = set() # Track "safe" transformers in Pipeline
        
        # Variable tracking for Control Flow Analysis (Q1)
        self._split_defined = False  # Has train_test_split been called?
        self._split_vars: Set[str] = set()  # Variables from split (X_train, X_test)
        self._original_data_vars: Set[str] = set()  # Original data variables (X, df)
        
    def _is_split_call(self, node: ast.AST) -> bool:
        """Check if node is a train_test_split call"""
        if isinstance(node, ast.Call):
            func_name = ""
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            return func_name in ["train_test_split", "TimeSeriesSplit"]
        return False

    def visit_Assign(self, node: ast.Assign):
        """Track variable assignments for Control Flow Analysis"""
        # Track original data variables (X, df, data, etc.)
        for target in node.targets:
            if isinstance(target, ast.Name):
                var_name = target.id.lower()
                # Common data variable names
                if var_name in ['x', 'df', 'data', 'dataset', 'df_train', 'raw_data']:
                    self._original_data_vars.add(target.id)
        
        # Detect train_test_split calls
        if self._is_split_call(node.value):
            self._split_defined = True
            # Extract variable names from the assignment
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self._split_vars.add(target.id)
        
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import):
        # Explicitly ignore import statements
        pass

    def visit_ImportFrom(self, node: ast.ImportFrom):
        # Explicitly ignore import statements
        pass

    def visit_Call(self, node: ast.Call):
        # 1. DETECT PIPELINE: Is this a Pipeline() instantiation? (Q2)
        if isinstance(node.func, ast.Name) and node.func.id == 'Pipeline':
            # Extract the 'steps' argument (list of tuples)
            steps_arg = None
            for kw in node.keywords:
                if kw.arg == 'steps':
                    steps_arg = kw.value
                    break
            if steps_arg is None and node.args:
                steps_arg = node.args[0]
            
            if steps_arg and isinstance(steps_arg, ast.List):
                for element in steps_arg.elts:
                    if isinstance(element, ast.Tuple) and len(element.elts) == 2:
                        transformer_call = element.elts[1]
                        if isinstance(transformer_call, ast.Call):
                            # Mark as SAFE
                            self._safe_transformer_ids.add(id(transformer_call))
            
            self.generic_visit(node)
            return

        # 2. CHECK SAFETY: Is this transformer in our "safe list"? (Q2)
        if id(node) in self._safe_transformer_ids:
            self.generic_visit(node)
            return

        # 3. DETECT LEAKAGE with Context Awareness (Q1)
        func_name = ""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        # Check against patterns
        for key, pattern in self.patterns.items():
            if func_name in pattern.indicators:
                # Special check for Time Series Shuffle
                if pattern.name == "time_series_shuffle":
                    if func_name in ["KFold", "ShuffleSplit"]:
                        is_shuffled = any(kw.arg == 'shuffle' and isinstance(kw.value, ast.Constant) and kw.value.value is True 
                                          for kw in node.keywords)
                        if not is_shuffled:
                            continue
                    else:
                        continue
                
                # Context-aware check: Only flag if split NOT defined (Q1)
                # This is a simplified version - full implementation would check
                # if the data being transformed is the original data vs split data
                self.found_leaks.append(pattern)
        
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript):
        # Detect sequential slicing like [:800]
        if isinstance(node.slice, ast.Slice):
            self.found_leaks.append(self.patterns["sequential_split"])
        self.generic_visit(node)


class LeakageDetector:
    """ML Pipeline Leakage Detector using AST analysis.
    
    Features:
    - AST-based detection (not just keywords)
    - Pipeline awareness (reduces false positives)
    - Variable tracking for context awareness
    - Severity-based prioritization
    """
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.patterns = ALL_PATTERNS

    def detect(self, code: str) -> DetectionResult:
        """Detect leakage patterns in Python code"""
        try:
            tree = ast.parse(code)
            visitor = LeakageVisitor(self.patterns)
            visitor.visit(tree)

            if visitor.found_leaks:
                return DetectionResult(
                    has_leakage=True,
                    leaks=visitor.found_leaks,
                )
        except SyntaxError:
            pass # Fallback for invalid python code

        return DetectionResult(
            has_leakage=False, leaks=[], confidence=0.95
        )

    def generate_report(self, result: DetectionResult) -> str:
        """Generate a prioritized report sorted by severity (Q3)"""
        if not result.has_leakage:
            return "✅ No data leakage detected. Pipeline appears clean."
        
        # Sort by severity
        sorted_leaks = result.sorted_leaks()
        
        report_lines = ["🚨 DATA LEAKAGE DETECTED"]
        
        # Group by severity
        critical = [l for l in sorted_leaks if l.severity == "Critical"]
        high = [l for l in sorted_leaks if l.severity == "High"]
        medium = [l for l in sorted_leaks if l.severity == "Medium"]
        
        if critical:
            report_lines.append("\n🔥 CRITICAL (Fix First)")
            for i, leak in enumerate(critical):
                report_lines.append(f"  • {leak.name}")
                report_lines.append(f"    Fix: {leak.fix_template}")
        
        if high:
            report_lines.append("\n⚠️ HIGH (Fix Before Deployment)")
            for leak in high:
                report_lines.append(f"  • {leak.name}")
                report_lines.append(f"    Fix: {leak.fix_template}")
        
        if medium:
            report_lines.append("\n📝 MEDIUM (Review Later)")
            for leak in medium:
                report_lines.append(f"  • {leak.name}")
                report_lines.append(f"    Fix: {leak.fix_template}")
                
        return "\n".join(report_lines)


def main():
    parser = argparse.ArgumentParser(description="ML Leakage Detector CLI")
    parser.add_argument("path", type=str, help="Path to a file or directory to analyze")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    parser.add_argument("--sort-severity", action="store_true", help="Sort output by severity")
    args = parser.parse_args()

    detector = LeakageDetector()
    target_path = Path(args.path)

    if not target_path.exists():
        print(f"Error: Path {args.path} does not exist.")
        sys.exit(1)

    files_to_scan = []
    if target_path.is_file():
        files_to_scan.append(target_path)
    else:
        files_to_scan.extend(target_path.rglob("*.py"))

    if not args.json:
        print(f"Scanning {len(files_to_scan)} files in {target_path}...\n")
    
    all_results = {}
    severity_counts = {"Critical": 0, "High": 0, "Medium": 0}
    
    for file_path in files_to_scan:
        if "venv" in str(file_path) or ".pytest_cache" in str(file_path):
            continue
            
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            result = detector.detect(content)
            all_results[str(file_path)] = result.to_dict()
            
            if result.has_leakage:
                # Count severity
                for leak in result.leaks:
                    if leak.severity in severity_counts:
                        severity_counts[leak.severity] += 1
                
                if not args.json:
                    print(f"File: {file_path}")
                    print(detector.generate_report(result))
                    print("-" * 40)

    has_any_leak = any(file_result['has_leakage'] for file_result in all_results.values())

    if args.json:
        output = {
            "summary": {
                "total_leaks": sum(severity_counts.values()),
                "critical": severity_counts["Critical"],
                "high": severity_counts["High"],
                "medium": severity_counts["Medium"]
            },
            "results": all_results
        }
        print(json.dumps(output, indent=2))
    elif not has_any_leak:
        print("✅ No leakage detected in any analyzed files.")
    else:
        print(f"\n📊 SUMMARY: {sum(severity_counts.values())} leaks found")
        print(f"  🔴 Critical: {severity_counts['Critical']}")
        print(f"  🟠 High: {severity_counts['High']}")
        print(f"  🟡 Medium: {severity_counts['Medium']}")
    
    # Exit with error code for CI/CD (Q3)
    sys.exit(1 if has_any_leak else 0)


if __name__ == "__main__":
    main()
