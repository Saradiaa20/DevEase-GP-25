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

#     return features
def extract_tabular_features(code: str, language: str = "python"):
    features = {}

    total_methods = 0
    total_classes = 0
    total_fields = 0
    total_variables = 0

    lang = language.lower()

    #  PYTHON (AST)
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

    #  JAVA (Regex)
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

    # derived features
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
    # SMART FEATURES
    features["is_singleton"] = 1 if "__new__" in code else 0
    features["has_clone"] = 1 if "clone(" in code  else 0
    features["many_classes"] = 1 if total_classes > 2 else 0
    return features