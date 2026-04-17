import os
from app.ml.parsing import ASTParser

def test_python_parsing():
    parser = ASTParser()
    
    file_path = os.path.join("test_files", "testfilepy.py")
    result = parser.parse_file(file_path)

    assert result["language"] == "Python"
    assert result["num_methods"] > 0
    assert result["cyclomatic_complexity"] > 0
    assert "_raw_source" in result

def test_java_parsing():
    parser = ASTParser()
    
    file_path = os.path.join("test_files", "SmellyClass.java")
    result = parser.parse_file(file_path)

    assert result["language"] == "Java"
    # If parsing failed → FAIL test clearly
    assert "error" not in result, f"Java parsing failed: {result.get('error')}"
    assert result["total_methods"] > 0
    assert result["lines_of_code"] > 0

def test_invalid_java():
    parser = ASTParser()

    # broken Java
    code = "public class Test { public void x( }"
    result = parser._parse_java_ast(code)

    assert "error" in result