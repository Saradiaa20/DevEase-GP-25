# """
# Extract tabular features for design-pattern ML inference.

# Training CSV may be either:
# - final_designpattern_dataset.csv (8 columns, no per-method complexity), or
# - final_dataset_clean.csv (10 columns including max_complexity, complexity_per_method).

# The saved feature_columns.pkl from training selects which keys are fed to the model at inference.
# """

# from __future__ import annotations

# import ast
# import re
# from typing import Any, Dict, List, Tuple


# def _cyclomatic_python(node: ast.AST) -> int:
#     """McCabe-style cyclomatic complexity for a function/method body."""
#     complexity = 1
#     for child in ast.walk(node):
#         if isinstance(
#             child,
#             (
#                 ast.If,
#                 ast.For,
#                 ast.AsyncFor,
#                 ast.While,
#                 ast.ExceptHandler,
#                 ast.With,
#                 ast.AsyncWith,
#                 ast.Assert,
#             ),
#         ):
#             complexity += 1
#         elif isinstance(child, ast.BoolOp):
#             complexity += len(child.values) - 1
#         elif isinstance(child, ast.comprehension):
#             complexity += 1
#     return complexity


# def _python_features(code: str) -> Tuple[List[int], int, int]:
#     """
#     Returns (per_function_cc_list, total_methods, total_classes).
#     """
#     try:
#         tree = ast.parse(code)
#     except SyntaxError:
#         return [], 0, 0

#     per_fn: List[int] = []
#     classes = 0

#     for node in ast.walk(tree):
#         if isinstance(node, ast.ClassDef):
#             classes += 1
#         if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
#             per_fn.append(_cyclomatic_python(node))

#     return per_fn, len(per_fn), classes


# def _java_method_blocks(code: str) -> List[str]:
#     """Rough split of Java/C-like code into method-like blocks for CC estimation."""
#     methods: List[str] = []
#     for m in re.finditer(
#         r"\b(public|private|protected)\s+[\w<>,\s]+\s+\w+\s*\([^)]*\)\s*\{",
#         code,
#     ):
#         start = m.start()
#         depth = 0
#         i = m.end() - 1
#         while i < len(code):
#             if code[i] == "{":
#                 depth += 1
#             elif code[i] == "}":
#                 depth -= 1
#                 if depth == 0:
#                     methods.append(code[m.start() : i + 1])
#                     break
#             i += 1
#     if not methods:
#         body = re.sub(r"//[^\n]*|/\*.*?\*/", "", code, flags=re.DOTALL)
#         if body.strip():
#             methods.append(body)
#     return methods


# def _cyclomatic_java_block(block: str) -> int:
#     text = re.sub(r"//[^\n]*|/\*.*?\*/", "", block)
#     complexity = 1
#     complexity += len(re.findall(r"\bif\s*\(", text))
#     complexity += len(re.findall(r"\bfor\s*\(", text))
#     complexity += len(re.findall(r"\bwhile\s*\(", text))
#     complexity += len(re.findall(r"\bcase\s+", text))
#     complexity += len(re.findall(r"\bcatch\s*\(", text))
#     complexity += len(re.findall(r"\belse\b", text))
#     complexity += len(re.findall(r"\|\|", text))
#     complexity += len(re.findall(r"\&\&", text))
#     complexity += text.count("?")
#     return complexity


# def _java_features(code: str) -> Tuple[List[int], int, int]:
#     blocks = _java_method_blocks(code)
#     if not blocks:
#         blocks = [code]
#     per_fn = [_cyclomatic_java_block(b) for b in blocks]
#     total_methods = len(per_fn)
#     total_classes = len(re.findall(r"\bclass\s+\w+", code))
#     return per_fn, total_methods, total_classes


# def _count_python_fields_vars(code: str, tree: ast.AST) -> Tuple[int, int]:
#     """Instance fields (self.x =) and local name bindings (approximate)."""
#     fields = len(re.findall(r"\bself\.\w+\s*=", code))
#     locals_ = 0
#     for node in ast.walk(tree):
#         if isinstance(node, ast.FunctionDef):
#             for stmt in node.body:
#                 if isinstance(stmt, ast.Assign):
#                     locals_ += len(stmt.targets)
#                 elif isinstance(stmt, ast.AnnAssign):
#                     locals_ += 1
#     return fields, locals_


# def _count_java_fields_vars(code: str) -> Tuple[int, int]:
#     fields = len(
#         re.findall(
#             r"\b(public|private|protected)\s+(static\s+)?(final\s+)?\w+\s+\w+\s*[;=]",
#             code,
#         )
#     )
#     vars_ = len(re.findall(r"\b(int|long|float|double|boolean|String|var|Object)\s+\w+\s*=", code))
#     return fields, vars_


# def extract_tabular_features(code_content: str, language: str) -> Dict[str, Any]:
#     """
#     Build all numeric features; training selects the subset listed in feature_columns.pkl.
#     """
#     lang = (language or "").strip().lower()
#     code = code_content or ""

#     if lang == "python":
#         per_fn, total_methods, total_classes = _python_features(code)
#         try:
#             tree = ast.parse(code)
#         except SyntaxError:
#             tree = None
#         if tree:
#             total_fields, total_variables = _count_python_fields_vars(code, tree)
#         else:
#             total_fields, total_variables = 0, 0
#     else:
#         per_fn, total_methods, total_classes = _java_features(code)
#         total_fields, total_variables = _count_java_fields_vars(code)

#     tc = max(total_classes, 0)
#     tm = max(total_methods, 0)

#     methods_per_class = tm // tc if tc else tm
#     fields_per_class = total_fields // tc if tc else total_fields
#     variables_per_class = total_variables // tc if tc else total_variables

#     if per_fn:
#         max_cc = min(100, max(per_fn))
#         total_cc = sum(per_fn)
#         complexity_per_method = total_cc // tm if tm else 0
#     else:
#         max_cc = 0
#         complexity_per_method = 0

#     size_score = tm + total_fields

#     return {
#         "total_methods": int(tm),
#         "total_classes": int(tc),
#         "total_fields": int(total_fields),
#         "total_variables": int(total_variables),
#         "methods_per_class": int(methods_per_class),
#         "fields_per_class": int(fields_per_class),
#         "variables_per_class": int(variables_per_class),
#         "max_complexity": int(max_cc),
#         "complexity_per_method": int(complexity_per_method),
#         "size_score": int(size_score),
#     }


# # Used by final_designpattern_dataset.csv (and default training target).
# FEATURE_COLUMN_ORDER = [
#     "total_methods",
#     "total_classes",
#     "total_fields",
#     "total_variables",
#     "methods_per_class",
#     "fields_per_class",
#     "variables_per_class",
#     "size_score",
# ]

# # Legacy 10-column layout (final_dataset_clean.csv) — for old checkpoints / alternate training only.
# FEATURE_COLUMN_ORDER_WITH_COMPLEXITY = [
#     "total_methods",
#     "total_classes",
#     "total_fields",
#     "total_variables",
#     "methods_per_class",
#     "fields_per_class",
#     "variables_per_class",
#     "max_complexity",
#     "complexity_per_method",
#     "size_score",
# ]


import ast
import re
FEATURE_COLUMN_ORDER = [
    "total_methods",
    "total_classes",
    "total_fields",
    "total_variables",
    "methods_per_class",
    "fields_per_class",
    "variables_per_class",
    "size_score",

 
]


# def extract_tabular_features(code: str, language: str = "Python"):
#     features = {}

#     total_methods = 0
#     total_classes = 0
#     total_fields = 0
#     total_variables = 0

#     try:
#         tree = ast.parse(code)

#         for node in ast.walk(tree):

#             # classes
#             if isinstance(node, ast.ClassDef):
#                 total_classes += 1

#                 # inheritance
#                 if node.bases:
#                     features["has_inheritance"] = 1

#             # methods
#             if isinstance(node, ast.FunctionDef):
#                 total_methods += 1

#             # variables
#             if isinstance(node, ast.Assign):
#                 total_variables += 1

#     except:
#         pass

#     if "has_inheritance" not in features:
#         features["has_inheritance"] = 0

#     total_fields = total_variables

#     # derived
#     methods_per_class = total_methods // total_classes if total_classes > 0 else 0
#     fields_per_class = total_fields // total_classes if total_classes > 0 else 0
#     variables_per_class = total_variables // total_classes if total_classes > 0 else 0

#     size_score = total_methods + total_fields

#     # =====================
#     # 🔥 SMART FEATURES
#     # =====================

#     # Singleton
#     features["is_singleton"] = 1 if "__new__" in code or "instance" in code else 0

#     # Prototype
#     features["has_clone"] = 1 if "copy(" in code or "clone(" in code else 0

#     # many classes
#     features["many_classes"] = 1 if total_classes > 2 else 0

#     # =====================

#     features.update({
#         "total_methods": total_methods,
#         "total_classes": total_classes,
#         "total_fields": total_fields,
#         "total_variables": total_variables,
#         "methods_per_class": methods_per_class,
#         "fields_per_class": fields_per_class,
#         "variables_per_class": variables_per_class,
#         "size_score": size_score,
#     })

#     return features
def extract_tabular_features(code: str, language: str = "python"):
    features = {}

    total_methods = 0
    total_classes = 0
    total_fields = 0
    total_variables = 0

    lang = language.lower()

    # =========================
    # 🟢 PYTHON (AST)
    # =========================
    if lang == "python":
        try:
            tree = ast.parse(code)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    total_classes += 1
                    if node.bases:
                        features["has_inheritance"] = 1

                if isinstance(node, ast.FunctionDef):
                    total_methods += 1

                if isinstance(node, ast.Assign):
                    total_variables += 1

        except:
            pass

    # =========================
    # 🔵 JAVA (Regex)
    # =========================
    else:
        # classes
        total_classes = len(re.findall(r"\bclass\s+\w+", code))

       # methods
        total_methods = len(re.findall(
            r"(public|private|protected)\s+(static\s+)?[\w<>\[\]]+\s+\w+\s*\(",
            code
        ))


        # fields
        total_fields = len(re.findall(
            r"(private|public|protected)\s+\w+\s+\w+\s*;",
            code
        ))

        # variables
        total_variables = len(re.findall(
            r"\b(int|String|double|float|boolean)\s+\w+\s*=",
            code
        ))

        # inheritance
        if "extends" in code or "implements" in code:
            features["has_inheritance"] = 1

    # default
    if "has_inheritance" not in features:
        features["has_inheritance"] = 0

    # =========================
    # derived features
    # =========================
    if total_classes == 0:
        methods_per_class = 0
        fields_per_class = 0
        variables_per_class = 0
    else:
        methods_per_class = total_methods // total_classes
        fields_per_class = total_fields // total_classes
        variables_per_class = total_variables // total_classes

    size_score = total_methods + total_fields

    features.update({
        "total_methods": total_methods,
        "total_classes": total_classes,
        "total_fields": total_fields,
        "total_variables": total_variables,
        "methods_per_class": methods_per_class,
        "fields_per_class": fields_per_class,
        "variables_per_class": variables_per_class,
        "size_score": size_score,
    })
    # 🔥 SMART FEATURES
    features["is_singleton"] = 1 if "__new__" in code else 0
    features["has_clone"] = 1 if "clone(" in code  else 0
    features["many_classes"] = 1 if total_classes > 2 else 0
    return features