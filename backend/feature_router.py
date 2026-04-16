"""
Feature Routing and Orchestration Module
Routes extracted features to various analysis modules and coordinates the analysis pipeline
"""

from typing import Dict, Any, Optional, List
import unicodedata
from parsing import ASTParser
from code_smell_detector import CodeSmellDetector
from code_quality_metrics import CodeQualityAnalyzer
from ml_complexity_predictor import ComplexityPredictor
from technical_debt_calculator import TechnicalDebtCalculator, TechnicalDebtMetrics
from design_pattern_detector import DesignPatternDetector
from nlp_explainer import generate_nlp_report
import os


class EmptyCodeError(ValueError):
    """Raised when a file or pasted content has no code to analyze (empty or whitespace-only)."""

    def __init__(
        self,
        message: str = "This file is empty or contains only whitespace. Upload a file with code to analyze.",
    ):
        super().__init__(message)


def _is_effectively_empty_code(text: Optional[str]) -> bool:
    """
    True if there is no real code: empty, only whitespace, BOM, zero-width/invisible
    Unicode (U+200B etc.), or other space/control/format characters.
    """
    if text is None:
        return True
    for ch in text.replace("\ufeff", ""):
        cat = unicodedata.category(ch)
        # Zs/Zl/Zp = separators; Cc = controls (newline, tab); Cf = format (ZWSP, etc.)
        if cat not in ("Zs", "Zl", "Zp", "Cc", "Cf"):
            return False
    return True


class FeatureRouter:
    """
    Orchestrates the analysis pipeline by routing features to appropriate modules
    """

    def __init__(self):
        self.ast_parser = ASTParser()
        self.smell_detector = CodeSmellDetector()
        self.quality_analyzer = CodeQualityAnalyzer()
        self.complexity_predictor = ComplexityPredictor()
        self.debt_calculator = TechnicalDebtCalculator()
        self.design_pattern_detector = DesignPatternDetector()
        # Try to load pre-trained design pattern model
        self.design_pattern_detector.load_model()

    def analyze_code(
        self,
        file_path: Optional[str] = None,
        code_content: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Complete analysis pipeline:
        1. Parse AST and extract features
        2. Route to code smell detection
        3. Route to quality metrics
        4. Route to ML complexity prediction
        5. Route to technical debt calculation
        6. Aggregate results

        Args:
            file_path: Path to code file
            code_content: Code content as string (if file_path not provided)

        Returns:
            Complete analysis results dictionary
        """
        # Step 1: Load content, reject empty / whitespace-only (no meaningful code to analyze)
        # FIX: corrected indentation — empty check and ast_result were wrongly nested
        # inside the 'with open' block in the original code.
        if file_path:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                code_content = f.read()
            if _is_effectively_empty_code(code_content):
                raise EmptyCodeError()
            ast_result = self.ast_parser.parse_file(file_path)
        elif code_content is not None:
            if _is_effectively_empty_code(code_content):
                raise EmptyCodeError()
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py', encoding='utf-8') as tmp:
                tmp.write(code_content)
                tmp_path = tmp.name

            try:
                ast_result = self.ast_parser.parse_file(tmp_path)
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
        else:
            raise ValueError("Either file_path or code_content must be provided")

        # Step 2: Extract features for ML model
        ml_features = self.complexity_predictor.extract_features_from_code(code_content)

        # Step 3: Route to code smell detection (AST-based)
        language = ast_result.get("language", "Unknown")

        if language == "Python":
            smells = self.smell_detector.detect_python_smells(ast_result)
        elif language == "Java":
            smells = self.smell_detector.detect_java_smells(ast_result)
        else:
            smells = []

        # FIX Bug 1 & Bug 2: smell_summary now includes 'total_smells' and 'smells' list.
        # Without 'total_smells', _calculate_smell_debt() always returned 0.0.
        # Without 'smells', _estimate_fix_hours() and _get_priority_issues() always
        # received an empty list, making those calculations completely wrong.
        smell_summary = {
            "by_type": {},
            "by_severity": {},
            "total_smells": len(smells),          # FIX Bug 1
            "smells": [                            # FIX Bug 2
                {
                    "type": s.smell_type,
                    "severity": s.severity,
                    "description": s.description,
                    "line": s.line_number,
                    "suggestion": s.suggestion
                }
                for s in smells
            ]
        }

        for s in smells:
            smell_summary["by_type"][s.smell_type] = (
                smell_summary["by_type"].get(s.smell_type, 0) + 1
            )
            smell_summary["by_severity"][s.severity] = (
                smell_summary["by_severity"].get(s.severity, 0) + 1
            )

        # Step 4: Route to quality metrics analysis
        if file_path:
            quality_score = self.quality_analyzer.analyze_file(file_path, smell_summary)
        else:
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py', encoding='utf-8') as tmp:
                tmp.write(code_content)
                tmp_path = tmp.name

            try:
                quality_score = self.quality_analyzer.analyze_file(tmp_path, smell_summary)
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)

        # Step 5: Route to ML complexity prediction
        ml_prediction = self.complexity_predictor.predict_complexity(ml_features)

        # Step 6: Route to technical debt calculation
        debt_metrics = self.debt_calculator.calculate_debt(
            quality_score={
                'overall_score': quality_score.overall_score,
                'maintainability': quality_score.maintainability,
                'readability': quality_score.readability,
                'complexity': quality_score.complexity,
                'documentation': quality_score.documentation,
                'issues': quality_score.issues,
                'recommendations': quality_score.recommendations
            },
            code_smells=smell_summary,
            ml_complexity={
                'features': ml_features,
                'prediction': ml_prediction
            },
            ast_data=ast_result
        )

        # Step 7: Route to design pattern detection
        language = ast_result.get('language', 'Unknown')
        design_patterns = self.design_pattern_detector.get_pattern_summary(code_content, language)

        # Step 8: Aggregate all results
        aggregated_results = {
            # Include actual code content for frontend display
            'code_content': code_content,

            # AST and parsing results
            'language': ast_result.get('language', 'Unknown'),
            'classes': ast_result.get('classes', []),
            'functions': ast_result.get('functions', []),
            'imports': ast_result.get('imports', []),
            'total_nodes': ast_result.get('total_nodes', 0),

            # Code smells
            'code_smells': [
                {
                    "type": s.smell_type,
                    "severity": s.severity,
                    "description": s.description,
                    "line": s.line_number,
                    "suggestion": s.suggestion
                }
                for s in smells
            ],

            # Quality metrics
            'quality_score': {
                'overall_score': quality_score.overall_score,
                'maintainability': quality_score.maintainability,
                'readability': quality_score.readability,
                'complexity': quality_score.complexity,
                'documentation': quality_score.documentation,
                'issues': quality_score.issues,
                'recommendations': quality_score.recommendations
            },

            # ML complexity prediction
            'ml_complexity': {
                'features': ml_features,
                'prediction': ml_prediction
            },

            # Technical debt
            'technical_debt': {
                'total_debt_score': debt_metrics.total_debt_score,
                'debt_level': self.debt_calculator._get_debt_level(debt_metrics.total_debt_score),
                'debt_breakdown': debt_metrics.debt_breakdown,
                'estimated_hours': debt_metrics.estimated_hours,
                'priority_issues': debt_metrics.priority_issues,
                'debt_severity': debt_metrics.debt_severity,
                'recommendations': debt_metrics.recommendations
            },

            # Design patterns (ML-based detection)
            'design_patterns': design_patterns.get('design_patterns', {}),

            # Analysis metadata
            'analysis_metadata': {
                'modules_used': [
                    'AST Parser',
                    'Code Smell Detector',
                    'Quality Metrics Analyzer',
                    'ML Complexity Predictor',
                    'Technical Debt Calculator',
                    'Design Pattern Detector'
                ],
                'analysis_complete': True
            }
        }

        aggregated_results['nlp_report'] = generate_nlp_report(aggregated_results)

        return aggregated_results

    def get_feature_summary(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Get a summary of extracted features"""
        return {
            'code_structure': {
                'language': analysis_results.get('language', 'Unknown'),
                'classes_count': len(analysis_results.get('classes', [])),
                'functions_count': len(analysis_results.get('functions', [])),
                'imports_count': len(analysis_results.get('imports', []))
            },
            'ml_features': analysis_results.get('ml_complexity', {}).get('features', {}),
            'smell_count': len(analysis_results.get('code_smells', [])),
            'quality_score': analysis_results.get('quality_score', {}).get('overall_score', 0),
            'technical_debt_score': analysis_results.get('technical_debt', {}).get('total_debt_score', 0)
        }
