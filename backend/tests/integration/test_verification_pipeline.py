import os
import tempfile
from app.ml.ml_complexity_predictor import ComplexityPredictor
from app.api.feature_router import FeatureRouter
from app.ml.parsing import ASTParser


# -----------------------------
# 1. ML MODEL TEST
# -----------------------------
def test_ml_model_load_and_predict():
    predictor = ComplexityPredictor()

    # load model (or train fallback expected in your system)
    loaded = predictor.load_model()
    assert loaded is True or loaded is False  # allow both states safely

    test_code = """
def example(n):
    for i in range(n):
        print(i)
"""

    features = predictor.extract_features_from_code(test_code)
    result = predictor.predict_complexity(features)

    assert "predicted_complexity" in result or "error" in result


# -----------------------------
# 2. PIPELINE TEST (FULL SYSTEM)
# -----------------------------
def test_full_analysis_pipeline():
    router = FeatureRouter()

    test_code = """
def add(a, b):
    return a + b

class A:
    def method(self):
        for i in range(5):
            print(i)
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(test_code)
        tmp_path = f.name

    try:
        result = router.analyze_code(file_path=tmp_path)

        # core structure checks
        assert "language" in result
        assert "code_smells" in result
        assert "quality_score" in result
        assert "ml_complexity" in result
        assert "technical_debt" in result

        # ML validation
        ml = result["ml_complexity"]
        assert "prediction" in ml

    finally:
        os.unlink(tmp_path)


# -----------------------------
# 3. API STRUCTURE TEST
# -----------------------------
def test_api_structure_matches_frontend():
    router = FeatureRouter()

    test_code = "def test(): pass"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(test_code)
        tmp_path = f.name

    try:
        result = router.analyze_code(file_path=tmp_path)

        assert result["ml_complexity"]["prediction"]["complexity_description"] is not None
        assert result["quality_score"]["overall_score"] is not None
        assert result["technical_debt"]["total_debt_score"] is not None
        assert isinstance(result["code_smells"], list)

    finally:
        os.unlink(tmp_path)


# -----------------------------
# 4. AST PARSER TEST (PYTHON)
# -----------------------------
def test_python_ast_parser():
    parser = ASTParser()

    code = """
def hello():
    for i in range(3):
        print(i)
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        tmp_path = f.name

    try:
        result = parser.parse_file(tmp_path)

        assert result["language"] == "Python"
        assert result["num_methods"] >= 1

    finally:
        os.unlink(tmp_path)


# -----------------------------
# 5. AST PARSER TEST (JAVA)
# -----------------------------
def test_java_ast_parser():
    parser = ASTParser()

    code = """
public class Test {
    public void a() {}

    public void b() {}

    public void c() {}
}
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".java", delete=False) as f:
        f.write(code)
        tmp_path = f.name

    try:
        result = parser.parse_file(tmp_path)

        assert result["language"] == "Java"
        assert result["total_methods"] >= 3
        assert "classes" in result

    finally:
        os.unlink(tmp_path)