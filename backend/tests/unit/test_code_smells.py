import os

from app.ml.code_smell_detector import CodeSmellDetector


# Helper function to load file content
def load_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# ---------------------------
# PYTHON TESTS (2 cases)
# ---------------------------

def test_python_smells_detected():
    detector = CodeSmellDetector()

    file_path = os.path.join( "test_files", "smelly_code.py")
    content = load_file(file_path)

    ast_data = {
        "_raw_source": content
    }

    smells = detector.detect_python_smells(ast_data)

    assert len(smells) > 0


def test_python_smell_types():
    detector = CodeSmellDetector()

    file_path = os.path.join( "test_files", "smelly_code.py")
    content = load_file(file_path)

    ast_data = {
        "_raw_source": content
    }

    detector.detect_python_smells(ast_data)
    summary = detector.get_smell_summary()

    # Check specific smells exist
    assert summary["by_type"].get("magic_number", 0) > 0
    assert summary["by_type"].get("long_parameter_list", 0) > 0


# ---------------------------
# JAVA TESTS (2 cases)
# ---------------------------

def test_java_smells_detected():
    detector = CodeSmellDetector()

    file_path = os.path.join("test_files", "SmellyClass.java")
    content = load_file(file_path)

    ast_data = {
        "_raw_source": content
    }

    smells = detector.detect_java_smells(ast_data)

    assert len(smells) > 0


def test_java_specific_smells():
    detector = CodeSmellDetector()

    file_path = os.path.join( "test_files", "SmellyClass.java")
    content = load_file(file_path)

    ast_data = {
        "_raw_source": content
    }

    detector.detect_java_smells(ast_data)
    summary = detector.get_smell_summary()

    # Check Java-specific smells
    assert summary["by_type"].get("long_parameter_list", 0) > 0
    assert summary["by_type"].get("println_in_domain", 0) > 0