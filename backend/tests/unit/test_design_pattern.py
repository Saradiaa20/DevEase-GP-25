import os
from app.ml.design_pattern_detector import DesignPatternDetector


def load_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


def test_model_loading():
    detector = DesignPatternDetector()
    assert detector.load_model() is True


def test_detect_pattern_from_java():
    detector = DesignPatternDetector()
    detector.load_model()

    file_path = os.path.join(BASE_DIR, "test_files", "SmellyClass.java")
    code = load_file(file_path)

    result = detector.get_pattern_summary(code, language="java")

    assert "design_patterns" in result
    assert "suggested_pattern" in result["design_patterns"]


def test_no_pattern_for_empty_code():
    detector = DesignPatternDetector()
    detector.load_model()

    result = detector.get_pattern_summary("", language="python")

    assert result["design_patterns"]["predicted_category"] in ["None", "Unknown"]

def test_design_pattern_on_bad_python_file():
    detector = DesignPatternDetector()
    detector.load_model()

    file_path = os.path.join(BASE_DIR, "test_files", "testfilepy.py")
    code = load_file(file_path)

    result = detector.get_pattern_summary(code, language="python")
    pattern_data = result["design_patterns"]

    # ✅ Assertions (robust)
    assert "suggested_pattern" in pattern_data
    assert "name" in pattern_data["suggested_pattern"]

    # Ensure it's not empty
    assert pattern_data["suggested_pattern"]["name"] is not None

    # Ensure category is valid
    assert pattern_data["predicted_category"] in [
        "Creational", "Structural", "Behavioral", "None", "Unknown"
    ]