"""
wrapper_detector.py
Wrapper Generator — Step 1: Pure AST / regex unsafe-pattern detection.
No AI involved here. Finds exactly what is wrong and where, so the
Groq prompt can be precise instead of generic.

Supports: Python (real AST via stdlib `ast`), Java (regex + heuristic).
"""

import ast
import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


# ─── Data model ──────────────────────────────────────────────────────────────

@dataclass
class UnsafePattern:
    pattern_id:   str
    pattern_type: str           # e.g. "bare_network_call"
    severity:     str           # "high" | "medium" | "low"
    line_number:  int
    end_line:     int
    code_snippet: str           # exact source lines of the unsafe block
    description:  str           # human-readable explanation
    context:      Dict[str, Any]
    language:     str


# ─── Python detector (real AST walk) ─────────────────────────────────────────

class _PythonDetector(ast.NodeVisitor):
    """Walk the Python AST and collect UnsafePattern objects."""

    NETWORK_CALLS = {
        "requests.get", "requests.post", "requests.put", "requests.delete",
        "requests.patch", "requests.head", "requests.request",
        "urllib.request.urlopen", "urllib.urlopen",
        "httpx.get", "httpx.post", "httpx.put", "httpx.delete",
        "aiohttp.ClientSession",
        "socket.connect", "socket.create_connection",
    }
    FILE_CALLS = {
        "open", "os.remove", "os.rename", "os.replace",
        "shutil.move", "shutil.copy", "shutil.copy2", "shutil.rmtree",
    }
    DB_CALLS = {
        "cursor.execute", "session.execute", "connection.execute",
        "db.execute", "engine.execute", "conn.execute",
    }
    SUBPROCESS_CALLS = {
        "subprocess.run", "subprocess.call", "subprocess.check_call",
        "subprocess.check_output", "subprocess.Popen",
        "os.system", "os.popen",
    }
    RISKY_CONVERSIONS = {"int", "float"}

    def __init__(self, source_lines: List[str]):
        self._lines = source_lines
        self.patterns: List[UnsafePattern] = []
        self._try_ranges: List[tuple] = []   # (start_line, end_line)

    # helpers -----------------------------------------------------------------

    def _snippet(self, node: ast.AST) -> str:
        s = node.lineno - 1
        e = getattr(node, "end_lineno", node.lineno)
        return "\n".join(self._lines[s:e])

    def _in_try(self, lineno: int) -> bool:
        return any(s <= lineno <= e for s, e in self._try_ranges)

    @staticmethod
    def _call_name(node: ast.Call) -> str:
        func = node.func
        if isinstance(func, ast.Attribute):
            v = func.value
            if isinstance(v, ast.Name):
                return f"{v.id}.{func.attr}"
            if isinstance(v, ast.Attribute) and isinstance(v.value, ast.Name):
                return f"{v.value.id}.{v.attr}.{func.attr}"
        if isinstance(func, ast.Name):
            return func.id
        return ""

    # visitors -----------------------------------------------------------------

    def visit_Try(self, node: ast.Try):
        self._try_ranges.append((node.lineno, node.end_lineno))
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        name = self._call_name(node)
        line = node.lineno
        end  = getattr(node, "end_lineno", line)

        if name in self.RISKY_CONVERSIONS and not self._in_try(line):
            # int()/float() can raise ValueError/TypeError on invalid input.
            self.patterns.append(UnsafePattern(
                pattern_id   = f"py_missing_try_catch_{line}",
                pattern_type = "missing_try_catch",
                severity     = "medium",
                line_number  = line,
                end_line     = end,
                code_snippet = self._snippet(node),
                description  = (
                    f"Type conversion `{name}(...)` at line {line} is not wrapped "
                    "in try/except. Invalid input can raise ValueError or TypeError."
                ),
                context  = {"call_name": name, "category": "error_handling"},
                language = "Python",
            ))

        elif name in self.NETWORK_CALLS and not self._in_try(line):
            self.patterns.append(UnsafePattern(
                pattern_id   = f"py_bare_network_{line}",
                pattern_type = "bare_network_call",
                severity     = "high",
                line_number  = line,
                end_line     = end,
                code_snippet = self._snippet(node),
                description  = (
                    f"Network call `{name}` at line {line} is not wrapped in "
                    "try/except. Network failures (timeout, DNS, HTTP errors) "
                    "will crash the program."
                ),
                context  = {"call_name": name, "category": "network"},
                language = "Python",
            ))

        elif name in self.FILE_CALLS and not self._in_try(line):
            self.patterns.append(UnsafePattern(
                pattern_id   = f"py_bare_file_{line}",
                pattern_type = "bare_file_operation",
                severity     = "medium",
                line_number  = line,
                end_line     = end,
                code_snippet = self._snippet(node),
                description  = (
                    f"File operation `{name}` at line {line} is not wrapped in "
                    "try/except. Missing files or permission errors are unhandled."
                ),
                context  = {"call_name": name, "category": "file_io"},
                language = "Python",
            ))

        elif name in self.DB_CALLS and not self._in_try(line):
            self.patterns.append(UnsafePattern(
                pattern_id   = f"py_bare_db_{line}",
                pattern_type = "bare_database_call",
                severity     = "high",
                line_number  = line,
                end_line     = end,
                code_snippet = self._snippet(node),
                description  = (
                    f"Database call `{name}` at line {line} is not protected "
                    "by try/except. DB errors or connection drops will propagate."
                ),
                context  = {"call_name": name, "category": "database"},
                language = "Python",
            ))

        elif name in self.SUBPROCESS_CALLS and not self._in_try(line):
            self.patterns.append(UnsafePattern(
                pattern_id   = f"py_bare_subprocess_{line}",
                pattern_type = "bare_subprocess_call",
                severity     = "medium",
                line_number  = line,
                end_line     = end,
                code_snippet = self._snippet(node),
                description  = (
                    f"Subprocess call `{name}` at line {line} may raise OSError "
                    "or CalledProcessError if the command fails."
                ),
                context  = {"call_name": name, "category": "subprocess"},
                language = "Python",
            ))

        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        """Detect swallowed exceptions (broad catch + pass)."""
        is_bare  = node.type is None
        is_broad = isinstance(node.type, ast.Name) and node.type.id == "Exception"
        body_pass = len(node.body) == 1 and isinstance(node.body[0], ast.Pass)

        if (is_bare or is_broad) and body_pass:
            self.patterns.append(UnsafePattern(
                pattern_id   = f"py_swallowed_exc_{node.lineno}",
                pattern_type = "swallowed_exception",
                severity     = "medium",
                line_number  = node.lineno,
                end_line     = getattr(node, "end_lineno", node.lineno),
                code_snippet = self._snippet(node),
                description  = (
                    f"Exception handler at line {node.lineno} silently swallows "
                    "errors with `pass`. This hides bugs and makes debugging hard."
                ),
                context  = {"category": "error_handling"},
                language = "Python",
            ))
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign):
        """Detect  f = open(...)  without `with` statement."""
        if isinstance(node.value, ast.Call):
            name = self._call_name(node.value)
            if name == "open" and not self._in_try(node.lineno):
                self.patterns.append(UnsafePattern(
                    pattern_id   = f"py_open_no_ctx_{node.lineno}",
                    pattern_type = "open_without_context_manager",
                    severity     = "medium",
                    line_number  = node.lineno,
                    end_line     = getattr(node, "end_lineno", node.lineno),
                    code_snippet = self._snippet(node),
                    description  = (
                        f"`open()` at line {node.lineno} is assigned to a variable "
                        "without a `with` statement. The file may not be closed if "
                        "an exception occurs."
                    ),
                    context  = {"category": "resource_management"},
                    language = "Python",
                ))
        self.generic_visit(node)


# ─── Java detector (regex + heuristic) ───────────────────────────────────────

class _JavaDetector:
    """
    Regex-based unsafe-pattern detector for Java.
    Uses a backwards-scan heuristic to decide if a line is inside a try block.
    """

    _HTTP = re.compile(
        r"(HttpURLConnection|HttpClient|OkHttpClient|RestTemplate|"
        r"WebClient|CloseableHttpClient|new\s+URL\s*\(|openConnection\s*\()"
    )
    _FILE = re.compile(
        r"(new\s+File\s*\(|Files\.(read|write|copy|move|delete|createFile|"
        r"newInputStream|newOutputStream)|FileInputStream|FileOutputStream|"
        r"BufferedReader|FileReader|FileWriter|PrintWriter)"
    )
    _DB = re.compile(
        r"(\.executeQuery\s*\(|\.executeUpdate\s*\(|\.execute\s*\(|"
        r"\.prepareStatement\s*\(|DriverManager\.getConnection)"
    )
    _CATCH_BROAD = re.compile(
        r"catch\s*\(\s*(Exception|Throwable)\s+\w+\s*\)"
    )

    def __init__(self, source_lines: List[str]):
        self._lines = source_lines
        self.patterns: List[UnsafePattern] = []

    def _snippet(self, i: int) -> str:
        return "\n".join(self._lines[i - 1: min(i + 2, len(self._lines))])

    def _in_try(self, line_idx: int) -> bool:
        depth = 0
        for i in range(line_idx, -1, -1):
            t = self._lines[i]
            depth += t.count("}") - t.count("{")
            if re.search(r"\btry\s*\{", t) and depth <= 0:
                return True
        return False

    def detect(self) -> List[UnsafePattern]:
        for i, line in enumerate(self._lines, 1):
            s = line.strip()
            if s.startswith("//") or s.startswith("*"):
                continue

            if self._HTTP.search(line) and not self._in_try(i):
                self.patterns.append(UnsafePattern(
                    pattern_id   = f"java_bare_http_{i}",
                    pattern_type = "bare_network_call",
                    severity     = "high",
                    line_number  = i, end_line = i,
                    code_snippet = self._snippet(i),
                    description  = (
                        f"HTTP/network operation at line {i} is not inside a "
                        "try-catch. IOException or runtime exceptions will propagate."
                    ),
                    context  = {"category": "network"},
                    language = "Java",
                ))

            elif self._FILE.search(line) and not self._in_try(i):
                self.patterns.append(UnsafePattern(
                    pattern_id   = f"java_bare_file_{i}",
                    pattern_type = "bare_file_operation",
                    severity     = "medium",
                    line_number  = i, end_line = i,
                    code_snippet = self._snippet(i),
                    description  = (
                        f"File operation at line {i} is not inside a try-catch. "
                        "FileNotFoundException or IOException may go unhandled."
                    ),
                    context  = {"category": "file_io"},
                    language = "Java",
                ))

            elif self._DB.search(line) and not self._in_try(i):
                self.patterns.append(UnsafePattern(
                    pattern_id   = f"java_bare_db_{i}",
                    pattern_type = "bare_database_call",
                    severity     = "high",
                    line_number  = i, end_line = i,
                    code_snippet = self._snippet(i),
                    description  = (
                        f"Database call at line {i} is outside a try-catch. "
                        "SQLException or connection errors will bubble up uncaught."
                    ),
                    context  = {"category": "database"},
                    language = "Java",
                ))

            if self._CATCH_BROAD.search(line):
                self.patterns.append(UnsafePattern(
                    pattern_id   = f"java_catch_broad_{i}",
                    pattern_type = "overly_broad_catch",
                    severity     = "low",
                    line_number  = i, end_line = i,
                    code_snippet = self._snippet(i),
                    description  = (
                        f"Catching `Exception` or `Throwable` at line {i} is overly "
                        "broad. Prefer catching specific exception types."
                    ),
                    context  = {"category": "error_handling"},
                    language = "Java",
                ))

        return self.patterns


# ─── Public API ──────────────────────────────────────────────────────────────

def detect_unsafe_patterns(code: str, language: str) -> List[UnsafePattern]:
    """
    Detect unsafe patterns in `code` for the given language.
    Returns a deduplicated list of UnsafePattern, sorted high → low severity.
    """
    lines = code.splitlines()

    if language == "Python":
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return []
        det = _PythonDetector(lines)
        det.visit(tree)
        patterns = det.patterns

    elif language == "Java":
        det = _JavaDetector(lines)
        patterns = det.detect()

    else:
        return []

    # Deduplicate by line number (keep first hit per line)
    seen: set = set()
    unique: List[UnsafePattern] = []
    for p in patterns:
        if p.line_number not in seen:
            seen.add(p.line_number)
            unique.append(p)

    order = {"high": 0, "medium": 1, "low": 2}
    unique.sort(key=lambda p: order.get(p.severity, 9))
    return unique


def patterns_to_dict(patterns: List[UnsafePattern]) -> List[Dict[str, Any]]:
    """Serialise for JSON responses."""
    return [
        {
            "pattern_id":   p.pattern_id,
            "pattern_type": p.pattern_type,
            "severity":     p.severity,
            "line_number":  p.line_number,
            "end_line":     p.end_line,
            "code_snippet": p.code_snippet,
            "description":  p.description,
            "context":      p.context,
            "language":     p.language,
        }
        for p in patterns
    ]
