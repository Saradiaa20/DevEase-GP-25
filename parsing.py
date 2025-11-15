
# parsing.py
import ast
import os
from code_smell_detector import CodeSmellDetector
from code_quality_metrics import CodeQualityAnalyzer
from ml_complexity_predictor import ComplexityPredictor

try:
    import javalang
except ImportError:
    javalang = None


class ASTParser:
    def __init__(self):
        self.smell_detector = CodeSmellDetector()
        self.quality_analyzer = CodeQualityAnalyzer()
        self.complexity_predictor = ComplexityPredictor()

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
        
        # Combine AST results with smell analysis, quality metrics, and ML prediction
        ast_result["code_smells"] = smell_summary
        ast_result["quality_score"] = quality_score
        ast_result["ml_complexity"] = ml_prediction
        
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
        tree = javalang.parse.parse(code)
        classes = [cls.name for cls in tree.types if hasattr(cls, 'name')]
        methods = [method.name for cls in tree.types for method in getattr(cls, 'methods', [])]
        fields = [field.declarators[0].name for cls in tree.types for field in getattr(cls, 'fields', [])]

        return {
            "language": "Java",
            "classes": classes,
            "methods": methods,
            "fields": fields,
            "total_classes": len(classes),
            "total_methods": len(methods)
        }
