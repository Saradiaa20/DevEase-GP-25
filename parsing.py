
# parsing.py
import ast
import os

try:
    import javalang
except ImportError:
    javalang = None


class ASTParser:
    def __init__(self):
        pass

    def parse_file(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        _, ext = os.path.splitext(file_path)

        with open(file_path, "r", encoding="utf-8") as file:
            code = file.read()

        if ext == ".py":
            return self._parse_python_ast(code)
        elif ext == ".java":
            if javalang is None:
                raise ImportError("Install javalang: pip install javalang")
            return self._parse_java_ast(code)
        else:
            raise ValueError(f"AST parsing not supported for {ext} files yet")

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
