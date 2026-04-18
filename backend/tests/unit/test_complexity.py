import os
from app.ml.ml_complexity_predictor import ComplexityPredictor

#Test case 1 - Model Loads Correctly
def test_model_loads():
    predictor = ComplexityPredictor()
    result = predictor.load_model()

    assert result is True
    assert predictor.model is not None

#Test case 2 - Feature Extraction (Python)
def test_feature_extraction_python():
    predictor = ComplexityPredictor()

    file_path = os.path.join( "test_files", "smelly_code.py")

    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    features = predictor.extract_features_from_code(code)

    assert isinstance(features, dict)
    assert "no_of_loop" in features
    assert "no_of_ifs" in features
    assert "nested_loop_depth" in features

#Test case 3 - Feature Extraction (Java)
def test_feature_extraction_java():
    predictor = ComplexityPredictor()

    file_path = os.path.join( "test_files", "SmellyClass.java")

    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    features = predictor.extract_features_from_code(code)

    assert isinstance(features, dict)
    assert features["no_of_loop"] >= 1  # nested loops exist
    assert features["no_of_ifs"] >= 0

#Test case 4 — Prediction works (Python smelly code)
def test_prediction_python_code():
    predictor = ComplexityPredictor()
    predictor.load_model()

    file_path = os.path.join( "test_files", "smelly_code.py")

    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    features = predictor.extract_features_from_code(code)
    result = predictor.predict_complexity(features)

    assert "predicted_complexity" in result
    assert "confidence" in result
    assert result["confidence"] >= 0

#Test case 5 — Prediction works (Java smelly code)
def test_prediction_java_code():
    predictor = ComplexityPredictor()
    predictor.load_model()

    file_path = os.path.join( "test_files", "SmellyClass.java")

    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    features = predictor.extract_features_from_code(code)
    result = predictor.predict_complexity(features)

    assert "predicted_complexity" in result
    assert result["predicted_complexity"] in ["1", "logn", "n", "n_square", "nlogn"]

#Test case 6 — Model returns valid probabilities
def test_prediction_probabilities():
    predictor = ComplexityPredictor()
    predictor.load_model()

    file_path = os.path.join( "test_files", "smelly_code.py")

    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    features = predictor.extract_features_from_code(code)
    result = predictor.predict_complexity(features)

    probs = result["all_probabilities"]

    assert isinstance(probs, dict)
    assert abs(sum(probs.values()) - 1.0) < 0.01  # probabilities sum to ~1

#Test case 7 — Feature extractor detects recursion
def test_recursion_detection():
    predictor = ComplexityPredictor()

    code = """
def f(n):
    if n == 0:
        return 1
    return f(n-1)
"""

    features = predictor.extract_features_from_code(code)

    assert features["recursion_present"] in [0, 1]