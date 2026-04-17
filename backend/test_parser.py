import os
from app.parsing import ASTParser

def test_python_parsing():
    parser = ASTParser()
    
    file_path = os.path.join("test_files", "clean_code.py")
    result = parser.parse_file(file_path)

    assert result["language"] == "Python"
    assert result["num_methods"] == 1
    assert result["num_classes"] == 0