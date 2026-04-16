import ast
import os
import sys
import argparse
from pathlib import Path
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from .patterns import ALL_PATTERNS, LeakagePattern


@dataclass
class DetectionResult:
    has_leakage: bool
    leaks: List[LeakagePattern] = field(default_factory=list)
    confidence: float = 0.95 # Overall confidence in the detection process

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class LeakageVisitor(ast.NodeVisitor):
    """AST Visitor to find potential leakage patterns in Python code."""
    def __init__(self, patterns: Dict[str, LeakagePattern]):
        self.patterns = patterns
        self.found_leaks = []
        self._safe_transformer_ids = set() # Store ids of AST nodes of transformers inside pipelines

    def visit_Import(self, node: ast.Import):
        # Explicitly ignore import statements like 'import StandardScaler'
        pass

    def visit_ImportFrom(self, node: ast.ImportFrom):
        # Explicitly ignore 'from sklearn import StandardScaler'
        pass

    def visit_Call(self, node: ast.Call):
        # First, check if this call is a Pipeline instantiation
        if isinstance(node.func, ast.Name) and node.func.id == 'Pipeline':
            for keyword in node.keywords:
                if keyword.arg == 'steps' and isinstance(keyword.value, ast.List):
                    for element in keyword.value.elts:
                        if isinstance(element, ast.Tuple) and len(element.elts) == 2:
                            # The second element of the tuple is the transformer instance
                            transformer_call = element.elts[1]
                            if isinstance(transformer_call, ast.Call):
                                self._safe_transformer_ids.add(id(transformer_call))
            # Don't process Pipeline itself for leakage patterns, but continue visiting its children
            self.generic_visit(node)
            return

        # If this call is a transformer that was identified as safe (inside a Pipeline), skip it
        if id(node) in self._safe_transformer_ids:
            self.generic_visit(node)
            return

        # Handle direct calls: StandardScaler()
        func_name = ""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        # Handle attribute calls: df.fillna()
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        for key, pattern in self.patterns.items():
            if func_name in pattern.indicators:
                # Special check for Time Series Shuffle
                if pattern.name == "time_series_shuffle":
                    if func_name in ["KFold", "ShuffleSplit"]:
                        is_shuffled = any(kw.arg == 'shuffle' and isinstance(kw.value, ast.Constant) and kw.value.value is True 
                                          for kw in node.keywords)
                        if not is_shuffled:
                            continue # Not a leak if shuffle=False or not specified
                    else:
                        continue
                
                self.found_leaks.append(pattern)
        
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript):
        # Detect sequential slicing like [:800]
        if isinstance(node.slice, ast.Slice):
            self.found_leaks.append(self.patterns["sequential_split"])
        self.generic_visit(node)


class LeakageDetector:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.patterns = ALL_PATTERNS

    def detect(self, code: str) -> DetectionResult:
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
            pass # Fallback or error handling for invalid python code

        return DetectionResult(
            has_leakage=False, leaks=[], confidence=0.95
        )

    def generate_report(self, result: DetectionResult) -> str:
        if not result.has_leakage:
            return "✅ No data leakage detected. Pipeline appears clean."
        
        report_lines = ["🚨 DATA LEAKAGE DETECTED"]
        for i, leak in enumerate(result.leaks):
            report_lines.append(f"--- Leak {i+1} ---")
            report_lines.append(f"Type: {leak.name} (Severity: {leak.severity})")
            report_lines.append(f"Description: {leak.description}")
            report_lines.append(f"Fix: {leak.fix_template}")
        return "\n".join(report_lines)


def main():
    parser = argparse.ArgumentParser(description="ML Leakage Detector CLI")
    parser.add_argument("path", type=str, help="Path to a file or directory to analyze")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
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
    for file_path in files_to_scan:
        if "venv" in str(file_path) or ".pytest_cache" in str(file_path):
            continue
            
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            result = detector.detect(content)
            all_results[str(file_path)] = result.to_dict()
            
            if result.has_leakage:
                if not args.json:
                    print(f"File: {file_path}")
                    print(detector.generate_report(result))
                    print("-" * 40)

    has_any_leak = any(file_result['has_leakage'] for file_result in all_results.values())

    if args.json:
        print(json.dumps(all_results, indent=2))
    elif not has_any_leak:
        print("✅ No leakage detected in any analyzed files.")
