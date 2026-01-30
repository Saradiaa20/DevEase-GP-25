
# parsing.py
import ast
import os
from code_smell_detector import CodeSmellDetector
from code_quality_metrics import CodeQualityAnalyzer
from ml_complexity_predictor import ComplexityPredictor
from technical_debt_calculator import TechnicalDebtCalculator

try:
    import javalang
except ImportError:
    javalang = None


class ASTParser:
    def __init__(self):
        self.smell_detector = CodeSmellDetector()
        self.quality_analyzer = CodeQualityAnalyzer()
        self.complexity_predictor = ComplexityPredictor()
        self.debt_calculator = TechnicalDebtCalculator()

    def parse_file(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        _, ext = os.path.splitext(file_path)

        with open(file_path, "r", encoding="utf-8") as file:
            code = file.read()

        # Parse AST structure (if supported)
        ast_result = {}
        if ext == ".py":
            ast_result = self._parse_python_ast(code)
        elif ext == ".java":
            if javalang is None:
                raise ImportError("Install javalang: pip install javalang")
            ast_result = self._parse_java_ast(code)
        else:
            # For unsupported AST languages, create basic structure
            ast_result = {
                "language": self._get_language_name(ext),
                "message": f"AST parsing not available for {ext} files, but code smell detection is active"
            }
        
        # Detect code smells (works for ALL supported file types)
        smells = self.smell_detector.detect_smells(file_path)
        smell_summary = self.smell_detector.get_smell_summary()
        
        # Analyze code quality (works for ALL supported file types)
        quality_score = self.quality_analyzer.analyze_file(file_path, smell_summary)
        
        # ML Complexity Prediction
        ml_prediction = self._predict_complexity(file_path)
        
        # Technical Debt Calculation
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
            ml_complexity=ml_prediction,
            ast_data=ast_result
        )
        
        # Combine AST results with smell analysis, quality metrics, ML prediction, and technical debt
        ast_result["code_smells"] = smell_summary
        ast_result["quality_score"] = quality_score
        ast_result["ml_complexity"] = ml_prediction
        ast_result["technical_debt"] = {
            'total_debt_score': debt_metrics.total_debt_score,
            'debt_level': self.debt_calculator._get_debt_level(debt_metrics.total_debt_score),
            'debt_breakdown': debt_metrics.debt_breakdown,
            'estimated_hours': debt_metrics.estimated_hours,
            'priority_issues': debt_metrics.priority_issues,
            'debt_trend': debt_metrics.debt_trend,
            'recommendations': debt_metrics.recommendations
        }
        
        return ast_result

    def _predict_complexity(self, file_path):
        """Predict code complexity using ML model"""
        try:
            # Read file content
            with open(file_path, "r", encoding="utf-8") as file:
                code_content = file.read()
            
            # Extract features from code
            features = self.complexity_predictor.extract_features_from_code(code_content)
            
            # Make prediction
            prediction = self.complexity_predictor.predict_complexity(features)
            
            return {
                "features": features,
                "prediction": prediction
            }
        except Exception as e:
            return {
                "error": f"ML prediction failed: {e}",
                "features": {},
                "prediction": {}
            }
    
    def _get_language_name(self, ext):
        """Get language name from file extension"""
        language_map = {
            '.py': 'Python',
            '.java': 'Java',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.cpp': 'C++',
            '.c': 'C',
            '.h': 'C/C++ Header',
            '.cs': 'C#',
            '.php': 'PHP'
        }
        return language_map.get(ext.lower(), 'Unknown')

    def _parse_python_ast(self, code):
        tree = ast.parse(code)

        classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        imports = [node.names[0].name for node in ast.walk(tree) if isinstance(node, ast.Import)]
        variables = [node.id for node in ast.walk(tree) if isinstance(node, ast.Name)]

        return {
            "language": "Python",
            "classes": classes,
            "functions": functions,
            "imports": imports,
            "variables": variables,
            "total_nodes": len(list(ast.walk(tree)))
        }

    def _parse_java_ast(self, code):
        try:
            tree = javalang.parse.parse(code)
            classes = [cls.name for cls in tree.types if hasattr(cls, 'name')]
            methods = [method.name for cls in tree.types for method in getattr(cls, 'methods', [])]
            fields = [field.declarators[0].name for cls in tree.types for field in getattr(cls, 'fields', [])]
            
            # Extract imports
            imports = []
            if tree.imports:
                for imp in tree.imports:
                    imports.append(imp.path)
            
            # Count total nodes by walking the tree
            total_nodes = 0
            for path, node in tree:
                total_nodes += 1

            return {
                "language": "Java",
                "classes": classes,
                "functions": methods,  # Use 'functions' to match frontend expectations
                "methods": methods,    # Keep 'methods' for backward compatibility
                "fields": fields,
                "imports": imports,
                "total_nodes": total_nodes,
                "total_classes": len(classes),
                "total_methods": len(methods)
            }
        except Exception as e:
            # Fallback to regex-based parsing for modern Java (Java 14+) features
            # that javalang doesn't support (switch expressions, text blocks, etc.)
            return self._parse_java_regex_fallback(code)
    
    def _parse_java_regex_fallback(self, code):
        """Regex-based fallback parser for modern Java code"""
        import re
        
        # Extract classes
        class_pattern = r'\bclass\s+(\w+)'
        classes = re.findall(class_pattern, code)
        
        # Extract methods (various patterns for Java methods)
        method_pattern = r'(?:public|private|protected|static|\s)+[\w<>\[\]]+\s+(\w+)\s*\([^)]*\)\s*(?:throws\s+[\w,\s]+)?\s*\{'
        methods = re.findall(method_pattern, code)
        # Filter out class names that might be caught as constructors
        methods = [m for m in methods if m not in classes and m not in ['if', 'while', 'for', 'switch', 'try', 'catch']]
        
        # Extract fields
        field_pattern = r'(?:private|protected|public)\s+(?:static\s+)?(?:final\s+)?[\w<>\[\]]+\s+(\w+)\s*[;=]'
        fields = re.findall(field_pattern, code)
        
        # Extract imports
        import_pattern = r'import\s+([\w.]+);'
        imports = re.findall(import_pattern, code)
        
        # Estimate total nodes based on code structure
        lines = code.split('\n')
        non_empty_lines = [l for l in lines if l.strip() and not l.strip().startswith('//')]
        total_nodes = len(non_empty_lines)
        
        return {
            "language": "Java",
            "classes": classes,
            "functions": methods,
            "methods": methods,
            "fields": fields,
            "imports": imports,
            "total_nodes": total_nodes,
            "total_classes": len(classes),
            "total_methods": len(methods),
            "parsing_method": "regex_fallback"  # Indicate fallback was used
        }
