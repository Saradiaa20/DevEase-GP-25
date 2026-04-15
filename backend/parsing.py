import ast
import os

from sklearn import tree
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

        # # Parse AST structure (if supported)
        # ast_result = {}
        # if ext == ".py":
        #     ast_result = self._parse_python_ast(code)
        # elif ext == ".java":
        #     if javalang is None:
        #         raise ImportError("Install javalang: pip install javalang")
        #     ast_result = self._parse_java_ast(code)
        # else:
        #     # For unsupported AST languages, create basic structure
        #     ast_result = {
        #         "language": self._get_language_name(ext),
        #         "message": f"AST parsing not available for {ext} files, but code smell detection is active"
        #     }
        
        # Detect code smells (works for ALL supported file types)
        # smells = self.smell_detector.detect_smells(file_path)
        # smell_summary = self.smell_detector.get_smell_summary()
        
        # AST-based analysis ONLY (no fallback)

        if ext == ".py":
            ast_result = self._parse_python_ast(code)
            smells = self.smell_detector.detect_python_smells(ast_result)

        elif ext == ".java":
            ast_result = self._parse_java_ast(code)

            if "error" in ast_result:
                return {
                    "error": "Java parsing failed. Analysis requires valid AST.",
                    "analysis_type": "failed"
                }

            smells = self.smell_detector.detect_java_smells(ast_result)
            print("SMELLS:", smells)
        else:
            return {
                "error": f"{ext} not supported for AST-based analysis",
                "analysis_type": "unsupported"
            }

            
        smell_summary = {
            "by_type": {},
            "by_severity": {}
        }

        for s in smells:
            # by_type
            smell_summary["by_type"][s.smell_type] = (
                smell_summary["by_type"].get(s.smell_type, 0) + 1
            )

            # by_severity
            smell_summary["by_severity"][s.severity] = (
                smell_summary["by_severity"].get(s.severity, 0) + 1
            )
        # Analyze code quality (works for ALL supported file types)
        quality_score = self.quality_analyzer.analyze_file(file_path, smell_summary)        # ML Complexity Prediction
        ml_prediction = self._predict_complexity(ast_result)
        
        # Combine AST results with smell analysis, quality metrics, and ML prediction
        # ast_result["code_smells"] = smells
        ast_result["code_smells"] = [
            {
                "type": s.smell_type,
                "severity": s.severity,
                "description": s.description,
                "line": s.line_number,
                "suggestion": s.suggestion
            }
            for s in smells
        ]
        ast_result["quality_score"] = quality_score
        ast_result["ml_complexity"] = ml_prediction
        ast_result["analysis_type"] = "AST-based"
        return ast_result

    def _predict_complexity(self, ast_result):
        """Predict code complexity using ML model"""
        try:
            # Read file content
            with open(ast_result, "r", encoding="utf-8") as file:
                code_content = file.read()
            
            # Extract features from code
            #features = self.complexity_predictor.extract_features_from_code(code_content)
            features = {
                "lines_of_code": ast_result.get("lines_of_code", 0),
                "cyclomatic_complexity": ast_result.get("cyclomatic_complexity", 0),
                "num_methods": ast_result.get("num_methods", 0),
                "num_classes": ast_result.get("num_classes", 0),
            }

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
            '.java': 'Java'
        }
        return language_map.get(ext.lower(), 'Unknown')

    def _compute_cyclomatic_complexity(self, tree):
        complexity = 1
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.And, ast.Or, ast.ExceptHandler, ast.With, ast.Try)):
                complexity += 1
        return complexity
    

    def _parse_python_ast(self, code):
        tree = ast.parse(code)
        cc = self._compute_cyclomatic_complexity(tree)

        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                 child.parent = node

        classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        # imports = [node.names[0].name for node in ast.walk(tree) if isinstance(node, ast.Import)]
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imports.append(alias.name)
        variables = [node.id for node in ast.walk(tree) if isinstance(node, ast.Name)]
        loops = sum(isinstance(n, (ast.For, ast.While)) for n in ast.walk(tree))
        ifs = sum(isinstance(n, ast.If) for n in ast.walk(tree))
        function_complexities = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                function_complexities[node.name] = self._compute_cyclomatic_complexity(node)

        return {
            "language": "Python",
            "classes": classes,
            "functions": functions,
            "imports": imports,
            "variables": variables,
            "total_nodes": len(list(ast.walk(tree))),
            "num_classes": len(classes),
            "num_methods": len(functions),
            "loops": loops,
            "ifs": ifs,
            "cyclomatic_complexity": cc,
            "lines_of_code": len(code.splitlines()),
            "function_complexities": function_complexities,
            "_raw_source": code
        }
    
    def _parse_java_ast(self, code):
        try:
            tree = javalang.parse.parse(code)
        except Exception:
            return {
                "language": "Java",
                "error": "Invalid or incomplete Java code"
            }

        classes = [cls.name for cls in tree.types if hasattr(cls, 'name')]
        methods = [method.name for cls in tree.types for method in getattr(cls, 'methods', [])]
        fields = [field.declarators[0].name for cls in tree.types for field in getattr(cls, 'fields', [])]
        total_nodes = 0
        for path, node in tree:
            total_nodes += 1
        return {
            "language": "Java",
            "classes": classes,
            "functions": methods,
            "methods": methods,
            "fields": fields,
            "total_nodes": total_nodes,
            "total_classes": len(classes),
            "total_methods": len(methods),
            "lines_of_code": len(code.splitlines()),
            "_raw_source": code
        }   