# # parsing.py
# import os
# import re

# class CodeParser:
#     SUPPORTED_LANGUAGES = {
#         '.py': 'Python',
#         '.java': 'Java',
#         '.js': 'JavaScript',
#         '.cpp': 'C++',
#         '.cs': 'C#',
#         '.php': 'PHP'
#     }

#     def __init__(self, file_path):
#         if not os.path.exists(file_path):
#             raise FileNotFoundError(f"File not found: {file_path}")
#         self.file_path = file_path
#         self.extension = os.path.splitext(file_path)[1]
#         self.language = self.SUPPORTED_LANGUAGES.get(self.extension, 'Unknown')
#         self.content = self._read_content()

#     def _read_content(self):
#         with open(self.file_path, 'r', encoding='utf-8') as file:
#             return file.read()

#     def count_lines(self):
#         return len(self.content.splitlines())

#     def count_comments(self):
#         single_comments = len(re.findall(r'^\s*(#|//)', self.content, re.MULTILINE))
#         multi_comments = len(re.findall(r'/\*.*?\*/', self.content, re.DOTALL))
#         return single_comments + multi_comments

#     def count_functions(self):
#         patterns = [
#             r'def\s+\w+\(',            # Python
#             r'\w+\s+\w+\s*\(',         # Java/C++/C#
#             r'function\s+\w+\('        # JavaScript/PHP
#         ]
#         total = 0
#         for pattern in patterns:
#             total += len(re.findall(pattern, self.content))
#         return total

#     def count_classes(self):
#         return len(re.findall(r'class\s+\w+', self.content))

#     def detect_todos(self):
#         return len(re.findall(r'(TODO|FIXME)', self.content))

#     def basic_code_smells(self):
#         smells = []
#         if self.count_lines() > 500:
#             smells.append("Large file (>500 lines)")
#         if any(len(line) > 120 for line in self.content.splitlines()):
#             smells.append("Long lines (>120 characters)")
#         if self.count_functions() > 50:
#             smells.append("Too many functions in one file")
#         return smells if smells else ["None"]

#     def summarize(self):
#         return {
#             "File": os.path.basename(self.file_path),
#             "Language": self.language,
#             "Total Lines": self.count_lines(),
#             "Comments": self.count_comments(),
#             "Functions": self.count_functions(),
#             "Classes": self.count_classes(),
#             "TODO Notes": self.detect_todos(),
#             "Code Smells": self.basic_code_smells()
#         }


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
