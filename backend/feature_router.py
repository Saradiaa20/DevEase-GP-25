"""
Feature Routing and Orchestration Module
Routes extracted features to various analysis modules and coordinates the analysis pipeline
"""

from typing import Dict, Any, Optional, List
from parsing import ASTParser
from code_smell_detector import CodeSmellDetector
from code_quality_metrics import CodeQualityAnalyzer
from ml_complexity_predictor import ComplexityPredictor
from technical_debt_calculator import TechnicalDebtCalculator, TechnicalDebtMetrics
from design_pattern_detector import DesignPatternDetector
import os

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
        # Step 1: Parse file and extract AST features
        if file_path:
            ast_result = self.ast_parser.parse_file(file_path)
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                code_content = f.read()
        elif code_content:
            # Create temporary file for parsing
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
        
        # Step 3: Route to code smell detection
        if file_path:
            smells = self.smell_detector.detect_smells(file_path)
        else:
            # Use temporary file for smell detection
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py', encoding='utf-8') as tmp:
                tmp.write(code_content)
                tmp_path = tmp.name
            
            try:
                smells = self.smell_detector.detect_smells(tmp_path)
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
        
        smell_summary = self.smell_detector.get_smell_summary()
        
        # Step 4: Route to quality metrics analysis
        if file_path:
            quality_score = self.quality_analyzer.analyze_file(file_path, smell_summary)
        else:
            # Use temporary file for quality analysis
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
        
        # Step 7: Route to design pattern detection (for Java code)
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
            'code_smells': smell_summary,
            
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
                'debt_trend': debt_metrics.debt_trend,
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
            'smell_count': analysis_results.get('code_smells', {}).get('total_smells', 0),
            'quality_score': analysis_results.get('quality_score', {}).get('overall_score', 0),
            'technical_debt_score': analysis_results.get('technical_debt', {}).get('total_debt_score', 0)
        }
