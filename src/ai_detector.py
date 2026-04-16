"""
AI-Enhanced ML Leakage Detector
================================

This module provides AI-powered features for the ML Leakage Detector:
1. AI Code Doctor - Generates fixes for detected leakage
2. NLP Auditor - Analyze code from natural language descriptions
3. Smart Context Analyzer - Reduces false positives
4. Pattern Discovery Engine - Finds new leakage patterns

Requires API keys:
- NVIDIA NGC (for Nemotron models) - REQUIRED
- Set environment variables in .env file

NVIDIA Models Available (free with NGC):
- nemotron-70b-instruct (best for code)
- llama-3.1-70b-instruct (excellent reasoning)
- mistral-7b-instruct (fast, lightweight)
"""

import os
import json
import ast
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

# NVIDIA NIM Configuration
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
BASE_URL = "https://integrate.api.nvidia.com/v1"

# Model preferences - NVIDIA NIM models (free with NGC)
MODELS = {
    "nemotron": "nvidia/nemotron-70b-instruct",  # Best for code
    "llama": "nvidia/llama-3.1-70b-instruct",     # Excellent reasoning
    "mistral": "nvidia/mistral-7b-instruct-v0.1", # Fast, lightweight
}

# Default model
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", MODELS["nemotron"])
FALLBACK_MODEL = os.getenv("FALLBACK_MODEL", MODELS["llama"])

# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class AIFix:
    """Represents an AI-generated fix for a leakage issue"""
    original_code: str
    fixed_code: str
    explanation: str
    confidence: float
    model_used: str


@dataclass
class NLPAnalysis:
    """Represents natural language analysis result"""
    has_leakage: bool
    leakage_type: str
    risk_level: str
    explanation: str
    recommended_fix: str


@dataclass
class ContextAnalysis:
    """Represents context-aware analysis"""
    is_legitimate: bool
    reason: str
    confidence: float
    context_details: str


@dataclass
class PatternDiscovery:
    """Represents a newly discovered pattern"""
    pattern_name: str
    description: str
    indicators: List[str]
    severity: str
    fix_suggestion: str
    confidence: float


# ============================================================================
# FEATURE 1: AI CODE DOCTOR (NVIDIA NIM / OpenAI)
# ============================================================================

class AICodeDoctor:
    """
    Feature 1: AI Code Doctor
    
    Uses NVIDIA NIM to generate specific code fixes for detected leakage.
    Supports multiple NVIDIA models.
    """
    
    def __init__(self, model: str = None):
        """
        Initialize AI Code Doctor
        
        Args:
            model: Model to use (nemotron, llama, mistral). Defaults to nemotron.
        """
        self.model_name = model or DEFAULT_MODEL
        self.client = None
        
        if NVIDIA_API_KEY:
            try:
                from openai import OpenAI
                self.client = OpenAI(
                    api_key=NVIDIA_API_KEY,
                    base_url=BASE_URL
                )
                logger.info(f"✅ AI Code Doctor initialized with {self.model_name}")
            except Exception as e:
                logger.warning(f"Failed to initialize AI client: {e}")
        else:
            logger.warning("⚠️ NVIDIA_API_KEY not set. AI features disabled.")
            logger.info("📝 Get your free key at: https://org.ngc.nvidia.com/")
    
    def generate_fix(self, leak_type: str, buggy_code: str, context: str = "") -> AIFix:
        """
        Generate a fix for the detected leakage
        
        Args:
            leak_type: Type of leakage (e.g., "imputation_before_split")
            buggy_code: The buggy code snippet
            context: Additional context about the pipeline
            
        Returns:
            AIFix object with fixed code and explanation
        """
        if not self.client:
            return AIFix(
                original_code=buggy_code,
                fixed_code="[AI Fix - API key not configured]",
                explanation="Please set OPENAI_API_KEY or NVIDIA_API_KEY",
                confidence=0.0,
                model_used="none"
            )
        
        # Build prompt based on leak type
        leak_info = self._get_leak_info(leak_type)
        
        prompt = f"""You are an expert ML engineer and code reviewer. 
The following code has a data leakage issue.

## LEAKAGE TYPE: {leak_type}
Description: {leak_info['description']}
Why it's dangerous: {leak_info['danger']}

## BUGGY CODE:
```python
{buggy_code}
```

{f"Context: {context}" if context else ""}

## TASK:
1. Identify what's wrong
2. Generate CORRECTED code that fixes the issue
3. Explain what was wrong and why the fix works

## OUTPUT FORMAT:
Provide your response in this exact format:
---
EXPLANATION: [Your explanation here]
FIXED_CODE:
```python
[Your fixed code here]
```"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content
            
            # Parse response
            explanation, fixed_code = self._parse_fix_response(content)
            
            return AIFix(
                original_code=buggy_code,
                fixed_code=fixed_code,
                explanation=explanation,
                confidence=0.85,
                model_used=self.model
            )
            
        except Exception as e:
            logger.error(f"Error generating fix: {e}")
            return AIFix(
                original_code=buggy_code,
                fixed_code=f"[Error: {str(e)}]",
                explanation="Failed to generate fix",
                confidence=0.0,
                model_used=self.model
            )
    
    def _get_leak_info(self, leak_type: str) -> Dict[str, str]:
        """Get information about a specific leak type"""
        leak_database = {
            "imputation_before_split": {
                "description": "Imputation (fillna, SimpleImputer) performed on full dataset",
                "danger": "Uses statistics from test set to fill training data"
            },
            "scaling_before_split": {
                "description": "Scaling (StandardScaler, MinMaxScaler) applied to full dataset",
                "danger": "Model sees global statistics before split"
            },
            "target_encoding_before_split": {
                "description": "Target encoding using full dataset",
                "danger": "Uses target variable to create features before split"
            },
            "feature_selection_before_split": {
                "description": "Feature selection using full dataset",
                "danger": "Selects features using test set labels"
            },
            "time_series_shuffle": {
                "description": "Shuffling time-series data during cross-validation",
                "danger": "Destroys temporal order, causing look-ahead bias"
            },
            "sequential_split": {
                "description": "Manual sequential slicing instead of random split",
                "danger": "May cause data leakage if data has temporal patterns"
            }
        }
        return leak_database.get(leak_type, {
            "description": "Unknown leakage pattern",
            "danger": "May cause model to perform poorly in production"
        })
    
    def _parse_fix_response(self, content: str) -> Tuple[str, str]:
        """Parse the AI response into explanation and fixed code"""
        lines = content.split('\n')
        explanation = []
        fixed_code = []
        in_code_block = False
        
        for line in lines:
            if line.startswith("EXPLANATION:"):
                continue
            elif line.startswith("FIXED_CODE:"):
                in_code_block = True
                continue
            elif line.startswith("```"):
                in_code_block = False
                continue
            else:
                if in_code_block:
                    fixed_code.append(line)
                elif line.strip():
                    explanation.append(line)
        
        return " ".join(explanation), "\n".join(fixed_code)


# ============================================================================
# FEATURE 2: NATURAL LANGUAGE AUDITOR
# ============================================================================

class NLPAuditor:
    """
    Feature 2: NLP Auditor
    
    Uses NVIDIA NIM to analyze code from natural language descriptions.
    Users can describe issues in plain English.
    """
    
    def __init__(self):
        if NVIDIA_API_KEY:
            try:
                from openai import OpenAI
                self.client = OpenAI(
                    api_key=NVIDIA_API_KEY,
                    base_url=BASE_URL
                )
                self.model = DEFAULT_MODEL
            except:
                self.client = None
        else:
            self.client = None
    
    def audit_description(self, description: str) -> NLPAnalysis:
        """
        Analyze a natural language description for potential leakage
        
        Args:
            description: User's description in plain English
            
        Returns:
            NLPAnalysis with findings
        """
        if not self.client:
            return NLPAnalysis(
                has_leakage=False,
                leakage_type="unknown",
                risk_level="Unknown",
                explanation="API key not configured",
                recommended_fix="Set OPENAI_API_KEY"
            )
        
        prompt = f"""You are an expert ML engineer specializing in detecting data leakage.
Analyze the following description for potential data leakage in ML pipelines.

## USER DESCRIPTION:
"{description}"

## TASK:
Analyze and return a JSON object with:
{{
    "has_leakage": true/false,
    "leakage_type": "type of leakage if any, or 'none'",
    "risk_level": "Critical/High/Medium/Low",
    "explanation": "Why this is/isn't leakage",
    "recommended_fix": "How to fix if leaky"
}}

Respond ONLY with valid JSON, no other text."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            
            # Parse JSON response
            result = json.loads(content.strip())
            
            return NLPAnalysis(
                has_leakage=result.get("has_leakage", False),
                leakage_type=result.get("leakage_type", "unknown"),
                risk_level=result.get("risk_level", "Unknown"),
                explanation=result.get("explanation", ""),
                recommended_fix=result.get("recommended_fix", "")
            )
            
        except Exception as e:
            logger.error(f"Error in NLP audit: {e}")
            return NLPAnalysis(
                has_leakage=False,
                leakage_type="error",
                risk_level="Unknown",
                explanation=str(e),
                recommended_fix="Retry later"
            )


# ============================================================================
# FEATURE 3: SMART CONTEXT ANALYZER
# ============================================================================

class SmartContextAnalyzer:
    """
    Feature 3: Smart Context Analyzer
    
    Uses NVIDIA NIM to analyze code context and reduce false positives.
    Determines if flagged code is actually safe based on usage.
    """
    
    def __init__(self):
        if NVIDIA_API_KEY:
            try:
                from openai import OpenAI
                self.client = OpenAI(
                    api_key=NVIDIA_API_KEY,
                    base_url=BASE_URL
                )
                self.model = DEFAULT_MODEL
            except:
                self.client = None
        else:
            self.client = None
    
    def analyze_context(
        self, 
        code: str, 
        flagged_pattern: str,
        full_code_context: str = ""
    ) -> ContextAnalysis:
        """
        Analyze if a flagged pattern is actually leakage
        
        Args:
            code: The specific code snippet flagged
            flagged_pattern: What pattern was detected
            full_code_context: The surrounding code for context
            
        Returns:
            ContextAnalysis with legitimacy determination
        """
        if not self.client:
            return ContextAnalysis(
                is_legitimate=False,
                reason="API key not configured",
                confidence=0.0,
                context_details="Unable to analyze without API key"
            )
        
        prompt = f"""You are a code analysis expert. Determine if the following code 
is actually data leakage or if there's a valid reason for its usage.

## FLAGGED CODE:
```python
{code}
```

## DETECTED PATTERN: {flagged_pattern}

{f"## SURROUNDING CODE:\n{full_code_context}" if full_code_context else ""}

## ANALYSIS CRITERIA:
Consider:
1. Is the data already split BEFORE this operation?
2. Is this inside a function that only receives training data?
3. Is this inside a sklearn Pipeline?
4. Is this computing statistics on train-only data?
5. Is this a test/evaluation code that legitimately needs full data?

## RESPONSE FORMAT:
Return ONLY this JSON:
{{
    "is_legitimate": true/false,
    "reason": "Explanation of your decision",
    "confidence": 0.0-1.0,
    "context_details": "Any specific context that justifies the code"
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            result = json.loads(content.strip())
            
            return ContextAnalysis(
                is_legitimate=result.get("is_legitimate", False),
                reason=result.get("reason", ""),
                confidence=result.get("confidence", 0.5),
                context_details=result.get("context_details", "")
            )
            
        except Exception as e:
            logger.error(f"Error in context analysis: {e}")
            return ContextAnalysis(
                is_legitimate=False,
                reason=str(e),
                confidence=0.0,
                context_details="Error occurred"
            )


# ============================================================================
# FEATURE 4: PATTERN DISCOVERY ENGINE
# ============================================================================

class PatternDiscoveryEngine:
    """
    Feature 4: Pattern Discovery Engine
    
    Uses NVIDIA NIM to analyze codebases and discover NEW leakage patterns
    that weren't previously defined.
    """
    
    def __init__(self):
        if NVIDIA_API_KEY:
            try:
                from openai import OpenAI
                self.client = OpenAI(
                    api_key=NVIDIA_API_KEY,
                    base_url=BASE_URL
                )
                self.model = FALLBACK_MODEL  # Use larger model for discovery
            except:
                self.client = None
        else:
            self.client = None
    
    def discover_patterns(self, codebase: str, known_patterns: List[str]) -> List[PatternDiscovery]:
        """
        Analyze a codebase to discover potential new leakage patterns
        
        Args:
            codebase: The Python code to analyze
            known_patterns: Patterns we already know about
            
        Returns:
            List of potentially new patterns
        """
        if not self.client:
            return []
        
        known_str = ", ".join(known_patterns)
        
        prompt = f"""You are an ML code analysis expert. Analyze the following 
Python code to find potential DATA LEAKAGE patterns that may not be 
in our known list.

## KNOWN PATTERNS (exclude these):
{known_str}

## CODEBASE TO ANALYZE:
```python
{codebase}
```

## TASK:
Look for ML operations that could cause leakage but aren't in our known list.
Consider:
- Custom preprocessing steps
- Database queries that might leak
- Feature engineering on full data
- Cross-validation issues
- Custom encoding schemes

## RESPONSE FORMAT:
Return a JSON array of potential new patterns, even if speculative:
[
    {{
        "pattern_name": "descriptive_name",
        "description": "what this pattern does",
        "indicators": ["keywords", "functions", "to", "detect"],
        "severity": "Critical/High/Medium",
        "fix_suggestion": "how to fix",
        "confidence": 0.0-1.0
    }}
]

If no new patterns found, return: []"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            results = json.loads(content.strip())
            
            if isinstance(results, list):
                return [
                    PatternDiscovery(
                        pattern_name=r.get("pattern_name", "unknown"),
                        description=r.get("description", ""),
                        indicators=r.get("indicators", []),
                        severity=r.get("severity", "Medium"),
                        fix_suggestion=r.get("fix_suggestion", ""),
                        confidence=r.get("confidence", 0.5)
                    )
                    for r in results
                ]
            return []
            
        except Exception as e:
            logger.error(f"Error in pattern discovery: {e}")
            return []


# ============================================================================
# UNIFIED AI DETECTOR
# ============================================================================

class AIDetector:
    """
    Unified AI Detector that combines all 4 features
    """
    
    def __init__(self):
        self.code_doctor = AICodeDoctor()
        self.nlp_auditor = NLPAuditor()
        self.context_analyzer = SmartContextAnalyzer()
        self.pattern_discovery = PatternDiscoveryEngine()
    
    def analyze_with_ai(
        self,
        code: str,
        detect_leakage: bool = True,
        generate_fixes: bool = True,
        analyze_context: bool = True,
        discover_patterns: bool = False
    ) -> Dict[str, Any]:
        """
        Perform comprehensive AI-enhanced analysis
        
        Args:
            code: Python code to analyze
            detect_leakage: Run standard detection + AI context
            generate_fixes: Generate AI fixes for issues
            analyze_context: Reduce false positives
            discover_patterns: Find new patterns
            
        Returns:
            Dictionary with all analysis results
        """
        results = {
            "ai_code_fixes": [],
            "nlp_audit": None,
            "context_analysis": [],
            "new_patterns": []
        }
        
        # Import here to avoid circular imports
        from src.detector import LeakageDetector
        
        # 1. Standard detection + Context analysis
        if detect_leakage or analyze_context:
            detector = LeakageDetector()
            standard_result = detector.detect(code)
            
            if standard_result.has_leakage:
                for leak in standard_result.leaks:
                    # Generate fix
                    if generate_fixes:
                        fix = self.code_doctor.generate_fix(
                            leak.name, 
                            code,
                            f"Detected {leak.description}"
                        )
                        results["ai_code_fixes"].append({
                            "leak_type": leak.name,
                            "fix": fix
                        })
                    
                    # Context analysis
                    if analyze_context:
                        context = self.context_analyzer.analyze_context(
                            code,
                            leak.name
                        )
                        results["context_analysis"].append({
                            "pattern": leak.name,
                            "analysis": context
                        })
        
        # 2. Pattern discovery
        if discover_patterns:
            known = [
                "imputation_before_split", "scaling_before_split",
                "sequential_split", "target_encoding_before_split",
                "feature_selection_before_split", "time_series_shuffle"
            ]
            patterns = self.pattern_discovery.discover_patterns(code, known)
            results["new_patterns"] = patterns
        
        return results


# ============================================================================
# CLI INTEGRATION
# ============================================================================

def main():
    """CLI for AI-powered leakage detection"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI-Enhanced ML Leakage Detector")
    parser.add_argument("path", type=str, help="Path to file or directory")
    parser.add_argument("--ai-fix", action="store_true", help="Generate AI fixes")
    parser.add_argument("--nlp", type=str, help="Natural language description to audit")
    parser.add_argument("--discover", action="store_true", help="Discover new patterns")
    parser.add_argument("--json", action="store_true", help="JSON output")
    
    args = parser.parse_args()
    
    # NLP Mode
    if args.nlp:
        auditor = NLPAuditor()
        result = auditor.audit_description(args.nlp)
        print(f"""
🔍 NLP Audit Results:
======================
Leakage Detected: {result.has_leakage}
Type: {result.leakage_type}
Risk Level: {result.risk_level}
Explanation: {result.explanation}
Fix: {result.recommended_fix}
""")
        return
    
    # File analysis mode
    from pathlib import Path
    from src.detector import LeakageDetector
    
    detector = LeakageDetector()
    target_path = Path(args.path)
    
    if target_path.is_file():
        with open(target_path) as f:
            code = f.read()
        
        results = AIDetector().analyze_with_ai(
            code,
            generate_fixes=args.ai_fix,
            discover_patterns=args.discover
        )
        
        if args.json:
            print(json.dumps(results, indent=2, default=lambda x: vars(x)))
        else:
            print(f"📊 Analysis for {target_path}")
            print("=" * 50)
            
            if results["ai_code_fixes"]:
                print(f"\n🤖 AI Code Fixes: {len(results['ai_code_fixes'])}")
                for fix in results["ai_code_fixes"]:
                    print(f"\n🔧 {fix['leak_type']}:")
                    print(f"   Explanation: {fix['fix'].explanation}")
                    print(f"   Fixed Code:\n{fix['fix'].fixed_code}")
            
            if results["new_patterns"]:
                print(f"\n🆕 New Patterns Discovered: {len(results['new_patterns'])}")
                for p in results["new_patterns"]:
                    print(f"   - {p.pattern_name} ({p.severity})")


if __name__ == "__main__":
    main()
