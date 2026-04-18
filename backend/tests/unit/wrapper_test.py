import pytest
from app.ml.wrapper_detector import (
    UnsafePattern,
    detect_unsafe_patterns,
    patterns_to_dict
)

class TestPythonDetector:
    
    def test_safe_code(self):
        code = """
try:
    x = int("10")
    r = requests.get("http://test.com")
    f = open("file.txt", "r")
    cursor.execute("SELECT 1")
    subprocess.run(["ls"])
except Exception as e:
    print(e)
"""
        patterns = detect_unsafe_patterns(code, "Python")
        assert len(patterns) == 0

    def test_missing_try_catch_conversion(self):
        code = "x = int(user_input)\n"
        patterns = detect_unsafe_patterns(code, "Python")
        assert len(patterns) == 1
        assert patterns[0].pattern_type == "missing_try_catch"
        assert patterns[0].severity == "medium"

    def test_bare_network_call(self):
        code = "response = requests.get('http://example.com')\n"
        patterns = detect_unsafe_patterns(code, "Python")
        assert len(patterns) == 1
        assert patterns[0].pattern_type == "bare_network_call"
        assert patterns[0].severity == "high"

    def test_bare_file_operation(self):
        code = "import shutil\nshutil.copy('a.txt', 'b.txt')\n"
        patterns = detect_unsafe_patterns(code, "Python")
        assert len(patterns) == 1
        assert patterns[0].pattern_type == "bare_file_operation"
        assert patterns[0].severity == "medium"

    def test_bare_db_call(self):
        code = "cursor.execute('DROP TABLE users')\n"
        patterns = detect_unsafe_patterns(code, "Python")
        assert len(patterns) == 1
        assert patterns[0].pattern_type == "bare_database_call"
        assert patterns[0].severity == "high"

    def test_bare_subprocess(self):
        code = "import os\nos.system('rm -rf /')\n"
        patterns = detect_unsafe_patterns(code, "Python")
        assert len(patterns) == 1
        assert patterns[0].pattern_type == "bare_subprocess_call"
        assert patterns[0].severity == "medium"

    def test_swallowed_exception(self):
        code = """
try:
    do_something()
except Exception:
    pass
"""
        patterns = detect_unsafe_patterns(code, "Python")
        assert len(patterns) == 1
        assert patterns[0].pattern_type == "swallowed_exception"
        assert patterns[0].severity == "medium"

    def test_open_without_context_manager(self):
        code = "f = open('test.txt')\n"
        patterns = detect_unsafe_patterns(code, "Python")
        assert len(patterns) >= 1

    def test_python_syntax_error(self):
        code = "def oops(:\n  print('bad')"
        patterns = detect_unsafe_patterns(code, "Python")
        assert patterns == []


class TestJavaDetector:

    def test_safe_java_code(self):
        code = """
public void doThing() {
    try {
        HttpClient client = new HttpClient();
        File f = new File("test.txt");
        stmt.executeQuery("SELECT 1");
    } catch (SpecificException e) {
        e.printStackTrace();
    }
}
"""
        patterns = detect_unsafe_patterns(code, "Java")
        assert len(patterns) == 0

    def test_java_overly_broad_catch(self):
        code = """
try {
    doWork();
} catch (Exception e) {
    System.out.println("Error");
}
"""
        patterns = detect_unsafe_patterns(code, "Java")
        assert len(patterns) == 1
        assert patterns[0].pattern_type == "overly_broad_catch"
        assert patterns[0].severity == "low"


class TestPublicAPI:

    def test_unsupported_language(self):
        code = "console.log('hello');"
        patterns = detect_unsafe_patterns(code, "JavaScript")
        assert patterns == []

    def test_sorting_and_deduplication(self):
        code = """
requests.get("url")
int("x")
        """
        patterns = detect_unsafe_patterns(code, "Python")
        assert len(patterns) == 2
        assert patterns[0].severity == "high"
        assert patterns[1].severity == "medium"

    def test_patterns_to_dict(self):
        code = "requests.get('url')\n"
        patterns = detect_unsafe_patterns(code, "Python")
        dict_patterns = patterns_to_dict(patterns)
        
        assert isinstance(dict_patterns, list)
        assert len(dict_patterns) == 1
        assert dict_patterns[0]["pattern_type"] == "bare_network_call"
        assert dict_patterns[0]["severity"] == "high"
        assert "line_number" in dict_patterns[0]
        assert "code_snippet" in dict_patterns[0]