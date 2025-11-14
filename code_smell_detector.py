import ast
import re
import os
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

@dataclass
class CodeSmell:
    """Represents a detected code smell with its details"""
    smell_type: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    description: str
    line_number: int
    suggestion: str

class CodeSmellDetector:
    """Detects various code smells in source code files"""
    
    def __init__(self):
        self.smells = []
        self.file_path = ""
        self.lines = []
    
    def detect_smells(self, file_path: str) -> List[CodeSmell]:
        """Main method to detect all code smells in a file"""
        self.smells = []
        self.file_path = file_path
        
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            self.lines = content.splitlines()
        
        _, ext = os.path.splitext(file_path)
        
        if ext == '.py':
            self._detect_python_smells(content)
        elif ext == '.java':
            self._detect_java_smells(content)
        elif ext in ['.js', '.ts']:
            self._detect_javascript_smells(content)
        elif ext in ['.cpp', '.c', '.h']:
            self._detect_cpp_smells(content)
        elif ext == '.cs':
            self._detect_csharp_smells(content)
        elif ext == '.php':
            self._detect_php_smells(content)
        
        # General smells that apply to all languages
        self._detect_general_smells(content)
        
        return self.smells
    
    def _detect_python_smells(self, content: str):
        """Detect Python-specific code smells"""
        try:
            tree = ast.parse(content)
            self._detect_long_functions(tree)
            self._detect_deep_nesting(tree)
            self._detect_duplicate_code_python(tree)
            self._detect_magic_numbers(content)
            self._detect_unused_imports(tree)
            self._detect_long_parameter_lists(tree)
            self._detect_complex_conditions(tree)
            self._detect_god_classes_python(tree)
        except SyntaxError:
            self.smells.append(CodeSmell(
                "syntax_error", "critical", "Syntax error in Python code", 0,
                "Fix syntax errors before analyzing code smells"
            ))
    
    def _detect_java_smells(self, content: str):
        """Detect Java-specific code smells"""
        self._detect_long_methods_java(content)
        self._detect_deep_nesting_java(content)
        self._detect_duplicate_code_java(content)
        self._detect_magic_numbers(content)
        self._detect_long_parameter_lists_java(content)
        self._detect_complex_conditions_java(content)
        self._detect_god_classes_java(content)
        self._detect_dead_code_java(content)
    
    def _detect_javascript_smells(self, content: str):
        """Detect JavaScript/TypeScript-specific code smells"""
        self._detect_long_functions_js(content)
        self._detect_deep_nesting_js(content)
        self._detect_duplicate_code_js(content)
        self._detect_magic_numbers(content)
        self._detect_callback_hell(content)
        self._detect_global_variables(content)
        self._detect_complex_conditions_js(content)
    
    def _detect_cpp_smells(self, content: str):
        """Detect C/C++-specific code smells"""
        self._detect_long_functions_cpp(content)
        self._detect_deep_nesting_cpp(content)
        self._detect_duplicate_code_cpp(content)
        self._detect_magic_numbers(content)
        self._detect_memory_leaks(content)
        self._detect_complex_conditions_cpp(content)
    
    def _detect_csharp_smells(self, content: str):
        """Detect C#-specific code smells"""
        self._detect_long_methods_csharp(content)
        self._detect_deep_nesting_csharp(content)
        self._detect_duplicate_code_csharp(content)
        self._detect_magic_numbers(content)
        self._detect_complex_conditions_csharp(content)
    
    def _detect_php_smells(self, content: str):
        """Detect PHP-specific code smells"""
        self._detect_long_functions_php(content)
        self._detect_deep_nesting_php(content)
        self._detect_duplicate_code_php(content)
        self._detect_magic_numbers(content)
        self._detect_complex_conditions_php(content)
    
    def _detect_general_smells(self, content: str):
        """Detect general code smells that apply to all languages"""
        self._detect_long_lines(content)
        self._detect_large_files(content)
        self._detect_comments_ratio(content)
        self._detect_todo_comments(content)
        self._detect_dead_code_general(content)
        self._detect_duplicate_strings(content)
        self._detect_hardcoded_values(content)
    
    # Python-specific smell detection methods
    def _detect_long_functions(self, tree):
        """Detect functions that are too long"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                start_line = node.lineno
                end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 20
                function_length = end_line - start_line + 1
                
                if function_length > 50:
                    severity = "high" if function_length > 100 else "medium"
                    self.smells.append(CodeSmell(
                        "long_function", severity,
                        f"Function '{node.name}' is {function_length} lines long",
                        start_line,
                        "Consider breaking this function into smaller, more focused functions"
                    ))
    
    def _detect_deep_nesting(self, tree):
        """Detect deeply nested code structures"""
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While, ast.If, ast.With, ast.Try)):
                nesting_level = self._calculate_nesting_level(node)
                if nesting_level > 4:
                    severity = "high" if nesting_level > 6 else "medium"
                    self.smells.append(CodeSmell(
                        "deep_nesting", severity,
                        f"Code block has {nesting_level} levels of nesting",
                        node.lineno,
                        "Consider extracting methods or using early returns to reduce nesting"
                    ))
    
    def _calculate_nesting_level(self, node):
        """Calculate the nesting level of a node"""
        level = 0
        current = node
        while hasattr(current, 'parent'):
            current = current.parent
            if isinstance(current, (ast.For, ast.While, ast.If, ast.With, ast.Try)):
                level += 1
        return level
    
    def _detect_duplicate_code_python(self, tree):
        """Detect duplicate code patterns in Python"""
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        
        for i, func1 in enumerate(functions):
            for func2 in functions[i+1:]:
                if self._functions_are_similar(func1, func2):
                    self.smells.append(CodeSmell(
                        "duplicate_code", "medium",
                        f"Functions '{func1.name}' and '{func2.name}' appear to be similar",
                        func1.lineno,
                        "Consider extracting common functionality into a shared function"
                    ))
    
    def _functions_are_similar(self, func1, func2):
        """Check if two functions are similar (simplified comparison)"""
        # This is a simplified comparison - in practice, you'd want more sophisticated analysis
        func1_lines = len([n for n in ast.walk(func1) if isinstance(n, (ast.Assign, ast.Call, ast.Return))])
        func2_lines = len([n for n in ast.walk(func2) if isinstance(n, (ast.Assign, ast.Call, ast.Return))])
        
        return abs(func1_lines - func2_lines) <= 2 and func1_lines > 5
    
    def _detect_magic_numbers(self, content: str):
        """Detect magic numbers in code"""
        # Look for numbers that aren't 0, 1, or common constants
        magic_number_pattern = r'\b(?<![\w.])([2-9]|[1-9]\d+)(?![\w.])\b'
        for match in re.finditer(magic_number_pattern, content):
            line_num = content[:match.start()].count('\n') + 1
            number = match.group(1)
            if int(number) > 10:  # Only flag numbers > 10 as potentially magic
                self.smells.append(CodeSmell(
                    "magic_number", "low",
                    f"Magic number '{number}' found",
                    line_num,
                    "Consider using a named constant instead of a magic number"
                ))
    
    def _detect_unused_imports(self, tree):
        """Detect unused imports in Python"""
        imports = []
        used_names = set()
        
        # Collect all imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append((alias.name, node.lineno))
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imports.append((alias.name, node.lineno))
            elif isinstance(node, ast.Name):
                used_names.add(node.id)
        
        # Check for unused imports
        for import_name, line_num in imports:
            if import_name not in used_names and not import_name.startswith('_'):
                self.smells.append(CodeSmell(
                    "unused_import", "low",
                    f"Unused import '{import_name}'",
                    line_num,
                    "Remove unused imports to clean up the code"
                ))
    
    def _detect_long_parameter_lists(self, tree):
        """Detect functions with too many parameters"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                param_count = len(node.args.args)
                if param_count > 5:
                    severity = "high" if param_count > 8 else "medium"
                    self.smells.append(CodeSmell(
                        "long_parameter_list", severity,
                        f"Function '{node.name}' has {param_count} parameters",
                        node.lineno,
                        "Consider using a data structure or object to group related parameters"
                    ))
    
    def _detect_complex_conditions(self, tree):
        """Detect complex conditional statements"""
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                condition_complexity = self._calculate_condition_complexity(node.test)
                if condition_complexity > 3:
                    severity = "high" if condition_complexity > 5 else "medium"
                    self.smells.append(CodeSmell(
                        "complex_condition", severity,
                        f"Complex condition with {condition_complexity} operators",
                        node.lineno,
                        "Consider extracting the condition into a well-named boolean method"
                    ))
    
    def _calculate_condition_complexity(self, node):
        """Calculate the complexity of a condition"""
        if isinstance(node, (ast.And, ast.Or)):
            return 1 + self._calculate_condition_complexity(node.left) + self._calculate_condition_complexity(node.right)
        elif isinstance(node, ast.Compare):
            return 1 + len(node.ops)
        else:
            return 1
    
    def _detect_god_classes_python(self, tree):
        """Detect classes that are too large or have too many responsibilities"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                attributes = [n for n in node.body if isinstance(n, ast.Assign)]
                
                if len(methods) > 15:
                    self.smells.append(CodeSmell(
                        "god_class", "high",
                        f"Class '{node.name}' has {len(methods)} methods",
                        node.lineno,
                        "Consider splitting this class into smaller, more focused classes"
                    ))
    
    # Java-specific smell detection methods
    def _detect_long_methods_java(self, content: str):
        """Detect long methods in Java"""
        method_pattern = r'(public|private|protected)?\s*(static)?\s*\w+\s+\w+\s*\([^)]*\)\s*\{'
        for match in re.finditer(method_pattern, content):
            start_line = content[:match.start()].count('\n') + 1
            method_end = self._find_method_end(content, match.end())
            method_length = method_end - start_line + 1
            
            if method_length > 50:
                severity = "high" if method_length > 100 else "medium"
                self.smells.append(CodeSmell(
                    "long_method", severity,
                    f"Method is {method_length} lines long",
                    start_line,
                    "Consider breaking this method into smaller, more focused methods"
                ))
    
    def _find_method_end(self, content, start_pos):
        """Find the end of a Java method"""
        brace_count = 0
        in_method = False
        
        for i, char in enumerate(content[start_pos:], start_pos):
            if char == '{':
                brace_count += 1
                in_method = True
            elif char == '}':
                brace_count -= 1
                if in_method and brace_count == 0:
                    return content[:i].count('\n') + 1
        
        return content.count('\n')
    
    def _detect_deep_nesting_java(self, content: str):
        """Detect deep nesting in Java code"""
        lines = content.split('\n')
        for i, line in enumerate(lines):
            nesting_level = len(re.findall(r'\{', line)) - len(re.findall(r'\}', line))
            if nesting_level > 4:
                self.smells.append(CodeSmell(
                    "deep_nesting", "medium",
                    f"Deep nesting detected (level {nesting_level})",
                    i + 1,
                    "Consider extracting methods or using early returns to reduce nesting"
                ))
    
    def _detect_duplicate_code_java(self, content: str):
        """Detect duplicate code in Java"""
        # This is a simplified implementation
        method_pattern = r'(public|private|protected)?\s*(static)?\s*\w+\s+\w+\s*\([^)]*\)\s*\{'
        methods = list(re.finditer(method_pattern, content))
        
        for i, method1 in enumerate(methods):
            for method2 in methods[i+1:]:
                method1_content = self._extract_method_content(content, method1)
                method2_content = self._extract_method_content(content, method2)
                
                if self._code_blocks_are_similar(method1_content, method2_content):
                    line_num = content[:method1.start()].count('\n') + 1
                    self.smells.append(CodeSmell(
                        "duplicate_code", "medium",
                        "Duplicate code detected between methods",
                        line_num,
                        "Consider extracting common functionality into a shared method"
                    ))
    
    def _extract_method_content(self, content, method_match):
        """Extract the content of a Java method"""
        start_pos = method_match.end()
        brace_count = 0
        in_method = False
        
        for i, char in enumerate(content[start_pos:], start_pos):
            if char == '{':
                brace_count += 1
                in_method = True
            elif char == '}':
                brace_count -= 1
                if in_method and brace_count == 0:
                    return content[start_pos:i+1]
        
        return ""
    
    def _code_blocks_are_similar(self, block1, block2):
        """Check if two code blocks are similar"""
        # Simplified similarity check based on line count and keywords
        lines1 = [line.strip() for line in block1.split('\n') if line.strip()]
        lines2 = [line.strip() for line in block2.split('\n') if line.strip()]
        
        if abs(len(lines1) - len(lines2)) > 2:
            return False
        
        # Check for common patterns
        keywords1 = set(re.findall(r'\b\w+\b', block1))
        keywords2 = set(re.findall(r'\b\w+\b', block2))
        
        common_keywords = len(keywords1.intersection(keywords2))
        total_keywords = len(keywords1.union(keywords2))
        
        return common_keywords / total_keywords > 0.7 if total_keywords > 0 else False
    
    def _detect_long_parameter_lists_java(self, content: str):
        """Detect long parameter lists in Java"""
        method_pattern = r'(public|private|protected)?\s*(static)?\s*\w+\s+\w+\s*\(([^)]*)\)'
        for match in re.finditer(method_pattern, content):
            params = match.group(3).strip()
            if params:
                param_count = len([p.strip() for p in params.split(',') if p.strip()])
                if param_count > 5:
                    severity = "high" if param_count > 8 else "medium"
                    line_num = content[:match.start()].count('\n') + 1
                    self.smells.append(CodeSmell(
                        "long_parameter_list", severity,
                        f"Method has {param_count} parameters",
                        line_num,
                        "Consider using a data structure or object to group related parameters"
                    ))
    
    def _detect_complex_conditions_java(self, content: str):
        """Detect complex conditions in Java"""
        if_pattern = r'if\s*\([^)]+\)'
        for match in re.finditer(if_pattern, content):
            condition = match.group(0)[3:-1]  # Remove 'if(' and ')'
            complexity = len(re.findall(r'(\&\&|\|\|)', condition))
            if complexity > 3:
                severity = "high" if complexity > 5 else "medium"
                line_num = content[:match.start()].count('\n') + 1
                self.smells.append(CodeSmell(
                    "complex_condition", severity,
                    f"Complex condition with {complexity} operators",
                    line_num,
                    "Consider extracting the condition into a well-named boolean method"
                ))
    
    def _detect_god_classes_java(self, content: str):
        """Detect god classes in Java"""
        class_pattern = r'class\s+\w+\s*\{'
        for match in re.finditer(class_pattern, content):
            class_start = match.end()
            class_end = self._find_class_end(content, class_start)
            class_content = content[class_start:class_end]
            
            method_count = len(re.findall(r'(public|private|protected)?\s*(static)?\s*\w+\s+\w+\s*\([^)]*\)\s*\{', class_content))
            field_count = len(re.findall(r'(public|private|protected)?\s*(static)?\s*(final)?\s*\w+\s+\w+;', class_content))
            
            if method_count > 15 or field_count > 20:
                line_num = content[:match.start()].count('\n') + 1
                self.smells.append(CodeSmell(
                    "god_class", "high",
                    f"Class has {method_count} methods and {field_count} fields",
                    line_num,
                    "Consider splitting this class into smaller, more focused classes"
                ))
    
    def _find_class_end(self, content, start_pos):
        """Find the end of a Java class"""
        brace_count = 0
        in_class = False
        
        for i, char in enumerate(content[start_pos:], start_pos):
            if char == '{':
                brace_count += 1
                in_class = True
            elif char == '}':
                brace_count -= 1
                if in_class and brace_count == 0:
                    return i
        
        return len(content)
    
    def _detect_dead_code_java(self, content: str):
        """Detect dead code in Java"""
        # Look for unreachable code after return statements
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'return' in line and not line.strip().startswith('//'):
                # Check if there's code after return in the same block
                j = i + 1
                while j < len(lines) and (lines[j].strip() == '' or lines[j].startswith('    ')):
                    if lines[j].strip() and not lines[j].strip().startswith('//'):
                        self.smells.append(CodeSmell(
                            "dead_code", "medium",
                            "Unreachable code after return statement",
                            j + 1,
                            "Remove unreachable code or restructure the logic"
                        ))
                    j += 1
    
    # JavaScript-specific smell detection methods
    def _detect_long_functions_js(self, content: str):
        """Detect long functions in JavaScript"""
        function_pattern = r'function\s+\w+\s*\([^)]*\)\s*\{|const\s+\w+\s*=\s*\([^)]*\)\s*=>\s*\{'
        for match in re.finditer(function_pattern, content):
            start_line = content[:match.start()].count('\n') + 1
            function_end = self._find_function_end_js(content, match.end())
            function_length = function_end - start_line + 1
            
            if function_length > 50:
                severity = "high" if function_length > 100 else "medium"
                self.smells.append(CodeSmell(
                    "long_function", severity,
                    f"Function is {function_length} lines long",
                    start_line,
                    "Consider breaking this function into smaller, more focused functions"
                ))
    
    def _find_function_end_js(self, content, start_pos):
        """Find the end of a JavaScript function"""
        brace_count = 0
        in_function = False
        
        for i, char in enumerate(content[start_pos:], start_pos):
            if char == '{':
                brace_count += 1
                in_function = True
            elif char == '}':
                brace_count -= 1
                if in_function and brace_count == 0:
                    return content[:i].count('\n') + 1
        
        return content.count('\n')
    
    def _detect_deep_nesting_js(self, content: str):
        """Detect deep nesting in JavaScript"""
        lines = content.split('\n')
        for i, line in enumerate(lines):
            nesting_level = len(re.findall(r'\{', line)) - len(re.findall(r'\}', line))
            if nesting_level > 4:
                self.smells.append(CodeSmell(
                    "deep_nesting", "medium",
                    f"Deep nesting detected (level {nesting_level})",
                    i + 1,
                    "Consider extracting functions or using early returns to reduce nesting"
                ))
    
    def _detect_duplicate_code_js(self, content: str):
        """Detect duplicate code in JavaScript"""
        function_pattern = r'function\s+\w+\s*\([^)]*\)\s*\{|const\s+\w+\s*=\s*\([^)]*\)\s*=>\s*\{'
        functions = list(re.finditer(function_pattern, content))
        
        for i, func1 in enumerate(functions):
            for func2 in functions[i+1:]:
                func1_content = self._extract_function_content_js(content, func1)
                func2_content = self._extract_function_content_js(content, func2)
                
                if self._code_blocks_are_similar(func1_content, func2_content):
                    line_num = content[:func1.start()].count('\n') + 1
                    self.smells.append(CodeSmell(
                        "duplicate_code", "medium",
                        "Duplicate code detected between functions",
                        line_num,
                        "Consider extracting common functionality into a shared function"
                    ))
    
    def _extract_function_content_js(self, content, func_match):
        """Extract the content of a JavaScript function"""
        start_pos = func_match.end()
        brace_count = 0
        in_function = False
        
        for i, char in enumerate(content[start_pos:], start_pos):
            if char == '{':
                brace_count += 1
                in_function = True
            elif char == '}':
                brace_count -= 1
                if in_function and brace_count == 0:
                    return content[start_pos:i+1]
        
        return ""
    
    def _detect_callback_hell(self, content: str):
        """Detect callback hell in JavaScript"""
        callback_pattern = r'\.then\s*\([^)]*\)\s*\.then\s*\([^)]*\)\s*\.then\s*\([^)]*\)'
        for match in re.finditer(callback_pattern, content):
            line_num = content[:match.start()].count('\n') + 1
            self.smells.append(CodeSmell(
                "callback_hell", "high",
                "Callback hell detected (multiple chained .then() calls)",
                line_num,
                "Consider using async/await or breaking down the promise chain"
            ))
    
    def _detect_global_variables(self, content: str):
        """Detect global variables in JavaScript"""
        global_var_pattern = r'var\s+\w+\s*=|let\s+\w+\s*=|const\s+\w+\s*='
        for match in re.finditer(global_var_pattern, content):
            line_num = content[:match.start()].count('\n') + 1
            # Check if it's at the top level (not inside a function)
            if self._is_global_scope(content, match.start()):
                self.smells.append(CodeSmell(
                    "global_variable", "medium",
                    "Global variable declaration detected",
                    line_num,
                    "Consider using modules or namespaces to avoid global scope pollution"
                ))
    
    def _is_global_scope(self, content, pos):
        """Check if a position is in global scope"""
        before_pos = content[:pos]
        function_opens = before_pos.count('{')
        function_closes = before_pos.count('}')
        return function_opens == function_closes
    
    def _detect_complex_conditions_js(self, content: str):
        """Detect complex conditions in JavaScript"""
        if_pattern = r'if\s*\([^)]+\)'
        for match in re.finditer(if_pattern, content):
            condition = match.group(0)[3:-1]
            complexity = len(re.findall(r'(\&\&|\|\|)', condition))
            if complexity > 3:
                severity = "high" if complexity > 5 else "medium"
                line_num = content[:match.start()].count('\n') + 1
                self.smells.append(CodeSmell(
                    "complex_condition", severity,
                    f"Complex condition with {complexity} operators",
                    line_num,
                    "Consider extracting the condition into a well-named function"
                ))
    
    # C++-specific smell detection methods
    def _detect_long_functions_cpp(self, content: str):
        """Detect long functions in C++"""
        function_pattern = r'\w+\s+\w+\s*\([^)]*\)\s*\{'
        for match in re.finditer(function_pattern, content):
            start_line = content[:match.start()].count('\n') + 1
            function_end = self._find_function_end_cpp(content, match.end())
            function_length = function_end - start_line + 1
            
            if function_length > 50:
                severity = "high" if function_length > 100 else "medium"
                self.smells.append(CodeSmell(
                    "long_function", severity,
                    f"Function is {function_length} lines long",
                    start_line,
                    "Consider breaking this function into smaller, more focused functions"
                ))
    
    def _find_function_end_cpp(self, content, start_pos):
        """Find the end of a C++ function"""
        brace_count = 0
        in_function = False
        
        for i, char in enumerate(content[start_pos:], start_pos):
            if char == '{':
                brace_count += 1
                in_function = True
            elif char == '}':
                brace_count -= 1
                if in_function and brace_count == 0:
                    return content[:i].count('\n') + 1
        
        return content.count('\n')
    
    def _detect_deep_nesting_cpp(self, content: str):
        """Detect deep nesting in C++"""
        lines = content.split('\n')
        for i, line in enumerate(lines):
            nesting_level = len(re.findall(r'\{', line)) - len(re.findall(r'\}', line))
            if nesting_level > 4:
                self.smells.append(CodeSmell(
                    "deep_nesting", "medium",
                    f"Deep nesting detected (level {nesting_level})",
                    i + 1,
                    "Consider extracting functions or using early returns to reduce nesting"
                ))
    
    def _detect_duplicate_code_cpp(self, content: str):
        """Detect duplicate code in C++"""
        function_pattern = r'\w+\s+\w+\s*\([^)]*\)\s*\{'
        functions = list(re.finditer(function_pattern, content))
        
        for i, func1 in enumerate(functions):
            for func2 in functions[i+1:]:
                func1_content = self._extract_function_content_cpp(content, func1)
                func2_content = self._extract_function_content_cpp(content, func2)
                
                if self._code_blocks_are_similar(func1_content, func2_content):
                    line_num = content[:func1.start()].count('\n') + 1
                    self.smells.append(CodeSmell(
                        "duplicate_code", "medium",
                        "Duplicate code detected between functions",
                        line_num,
                        "Consider extracting common functionality into a shared function"
                    ))
    
    def _extract_function_content_cpp(self, content, func_match):
        """Extract the content of a C++ function"""
        start_pos = func_match.end()
        brace_count = 0
        in_function = False
        
        for i, char in enumerate(content[start_pos:], start_pos):
            if char == '{':
                brace_count += 1
                in_function = True
            elif char == '}':
                brace_count -= 1
                if in_function and brace_count == 0:
                    return content[start_pos:i+1]
        
        return ""
    
    def _detect_memory_leaks(self, content: str):
        """Detect potential memory leaks in C++"""
        # Look for new without delete
        new_pattern = r'new\s+\w+'
        delete_pattern = r'delete\s+'
        
        new_matches = list(re.finditer(new_pattern, content))
        delete_matches = list(re.finditer(delete_pattern, content))
        
        if len(new_matches) > len(delete_matches):
            for match in new_matches:
                line_num = content[:match.start()].count('\n') + 1
                self.smells.append(CodeSmell(
                    "potential_memory_leak", "high",
                    "Potential memory leak: 'new' without corresponding 'delete'",
                    line_num,
                    "Ensure all 'new' allocations have corresponding 'delete' statements"
                ))
    
    def _detect_complex_conditions_cpp(self, content: str):
        """Detect complex conditions in C++"""
        if_pattern = r'if\s*\([^)]+\)'
        for match in re.finditer(if_pattern, content):
            condition = match.group(0)[3:-1]
            complexity = len(re.findall(r'(\&\&|\|\|)', condition))
            if complexity > 3:
                severity = "high" if complexity > 5 else "medium"
                line_num = content[:match.start()].count('\n') + 1
                self.smells.append(CodeSmell(
                    "complex_condition", severity,
                    f"Complex condition with {complexity} operators",
                    line_num,
                    "Consider extracting the condition into a well-named function"
                ))
    
    # C#-specific smell detection methods
    def _detect_long_methods_csharp(self, content: str):
        """Detect long methods in C#"""
        method_pattern = r'(public|private|protected|internal)?\s*(static)?\s*\w+\s+\w+\s*\([^)]*\)\s*\{'
        for match in re.finditer(method_pattern, content):
            start_line = content[:match.start()].count('\n') + 1
            method_end = self._find_method_end_csharp(content, match.end())
            method_length = method_end - start_line + 1
            
            if method_length > 50:
                severity = "high" if method_length > 100 else "medium"
                self.smells.append(CodeSmell(
                    "long_method", severity,
                    f"Method is {method_length} lines long",
                    start_line,
                    "Consider breaking this method into smaller, more focused methods"
                ))
    
    def _find_method_end_csharp(self, content, start_pos):
        """Find the end of a C# method"""
        brace_count = 0
        in_method = False
        
        for i, char in enumerate(content[start_pos:], start_pos):
            if char == '{':
                brace_count += 1
                in_method = True
            elif char == '}':
                brace_count -= 1
                if in_method and brace_count == 0:
                    return content[:i].count('\n') + 1
        
        return content.count('\n')
    
    def _detect_deep_nesting_csharp(self, content: str):
        """Detect deep nesting in C#"""
        lines = content.split('\n')
        for i, line in enumerate(lines):
            nesting_level = len(re.findall(r'\{', line)) - len(re.findall(r'\}', line))
            if nesting_level > 4:
                self.smells.append(CodeSmell(
                    "deep_nesting", "medium",
                    f"Deep nesting detected (level {nesting_level})",
                    i + 1,
                    "Consider extracting methods or using early returns to reduce nesting"
                ))
    
    def _detect_duplicate_code_csharp(self, content: str):
        """Detect duplicate code in C#"""
        method_pattern = r'(public|private|protected|internal)?\s*(static)?\s*\w+\s+\w+\s*\([^)]*\)\s*\{'
        methods = list(re.finditer(method_pattern, content))
        
        for i, method1 in enumerate(methods):
            for method2 in methods[i+1:]:
                method1_content = self._extract_method_content_csharp(content, method1)
                method2_content = self._extract_method_content_csharp(content, method2)
                
                if self._code_blocks_are_similar(method1_content, method2_content):
                    line_num = content[:method1.start()].count('\n') + 1
                    self.smells.append(CodeSmell(
                        "duplicate_code", "medium",
                        "Duplicate code detected between methods",
                        line_num,
                        "Consider extracting common functionality into a shared method"
                    ))
    
    def _extract_method_content_csharp(self, content, method_match):
        """Extract the content of a C# method"""
        start_pos = method_match.end()
        brace_count = 0
        in_method = False
        
        for i, char in enumerate(content[start_pos:], start_pos):
            if char == '{':
                brace_count += 1
                in_method = True
            elif char == '}':
                brace_count -= 1
                if in_method and brace_count == 0:
                    return content[start_pos:i+1]
        
        return ""
    
    def _detect_complex_conditions_csharp(self, content: str):
        """Detect complex conditions in C#"""
        if_pattern = r'if\s*\([^)]+\)'
        for match in re.finditer(if_pattern, content):
            condition = match.group(0)[3:-1]
            complexity = len(re.findall(r'(\&\&|\|\|)', condition))
            if complexity > 3:
                severity = "high" if complexity > 5 else "medium"
                line_num = content[:match.start()].count('\n') + 1
                self.smells.append(CodeSmell(
                    "complex_condition", severity,
                    f"Complex condition with {complexity} operators",
                    line_num,
                    "Consider extracting the condition into a well-named method"
                ))
    
    # PHP-specific smell detection methods
    def _detect_long_functions_php(self, content: str):
        """Detect long functions in PHP"""
        function_pattern = r'function\s+\w+\s*\([^)]*\)\s*\{'
        for match in re.finditer(function_pattern, content):
            start_line = content[:match.start()].count('\n') + 1
            function_end = self._find_function_end_php(content, match.end())
            function_length = function_end - start_line + 1
            
            if function_length > 50:
                severity = "high" if function_length > 100 else "medium"
                self.smells.append(CodeSmell(
                    "long_function", severity,
                    f"Function is {function_length} lines long",
                    start_line,
                    "Consider breaking this function into smaller, more focused functions"
                ))
    
    def _find_function_end_php(self, content, start_pos):
        """Find the end of a PHP function"""
        brace_count = 0
        in_function = False
        
        for i, char in enumerate(content[start_pos:], start_pos):
            if char == '{':
                brace_count += 1
                in_function = True
            elif char == '}':
                brace_count -= 1
                if in_function and brace_count == 0:
                    return content[:i].count('\n') + 1
        
        return content.count('\n')
    
    def _detect_deep_nesting_php(self, content: str):
        """Detect deep nesting in PHP"""
        lines = content.split('\n')
        for i, line in enumerate(lines):
            nesting_level = len(re.findall(r'\{', line)) - len(re.findall(r'\}', line))
            if nesting_level > 4:
                self.smells.append(CodeSmell(
                    "deep_nesting", "medium",
                    f"Deep nesting detected (level {nesting_level})",
                    i + 1,
                    "Consider extracting functions or using early returns to reduce nesting"
                ))
    
    def _detect_duplicate_code_php(self, content: str):
        """Detect duplicate code in PHP"""
        function_pattern = r'function\s+\w+\s*\([^)]*\)\s*\{'
        functions = list(re.finditer(function_pattern, content))
        
        for i, func1 in enumerate(functions):
            for func2 in functions[i+1:]:
                func1_content = self._extract_function_content_php(content, func1)
                func2_content = self._extract_function_content_php(content, func2)
                
                if self._code_blocks_are_similar(func1_content, func2_content):
                    line_num = content[:func1.start()].count('\n') + 1
                    self.smells.append(CodeSmell(
                        "duplicate_code", "medium",
                        "Duplicate code detected between functions",
                        line_num,
                        "Consider extracting common functionality into a shared function"
                    ))
    
    def _extract_function_content_php(self, content, func_match):
        """Extract the content of a PHP function"""
        start_pos = func_match.end()
        brace_count = 0
        in_function = False
        
        for i, char in enumerate(content[start_pos:], start_pos):
            if char == '{':
                brace_count += 1
                in_function = True
            elif char == '}':
                brace_count -= 1
                if in_function and brace_count == 0:
                    return content[start_pos:i+1]
        
        return ""
    
    def _detect_complex_conditions_php(self, content: str):
        """Detect complex conditions in PHP"""
        if_pattern = r'if\s*\([^)]+\)'
        for match in re.finditer(if_pattern, content):
            condition = match.group(0)[3:-1]
            complexity = len(re.findall(r'(\&\&|\|\|)', condition))
            if complexity > 3:
                severity = "high" if complexity > 5 else "medium"
                line_num = content[:match.start()].count('\n') + 1
                self.smells.append(CodeSmell(
                    "complex_condition", severity,
                    f"Complex condition with {complexity} operators",
                    line_num,
                    "Consider extracting the condition into a well-named function"
                ))
    
    # General smell detection methods
    def _detect_long_lines(self, content: str):
        """Detect lines that are too long"""
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if len(line) > 120:
                severity = "high" if len(line) > 200 else "medium"
                self.smells.append(CodeSmell(
                    "long_line", severity,
                    f"Line is {len(line)} characters long",
                    i + 1,
                    "Consider breaking long lines for better readability"
                ))
    
    def _detect_large_files(self, content: str):
        """Detect files that are too large"""
        line_count = len(content.split('\n'))
        if line_count > 500:
            severity = "high" if line_count > 1000 else "medium"
            self.smells.append(CodeSmell(
                "large_file", severity,
                f"File has {line_count} lines",
                1,
                "Consider splitting this file into smaller, more focused files"
            ))
    
    def _detect_comments_ratio(self, content: str):
        """Detect files with too few or too many comments"""
        lines = content.split('\n')
        total_lines = len(lines)
        comment_lines = len([line for line in lines if line.strip().startswith(('#', '//', '/*', '*'))])
        
        if total_lines > 10:  # Only check files with more than 10 lines
            comment_ratio = comment_lines / total_lines
            if comment_ratio < 0.1:  # Less than 10% comments
                self.smells.append(CodeSmell(
                    "low_comment_ratio", "low",
                    f"Only {comment_ratio:.1%} of lines are comments",
                    1,
                    "Consider adding more comments to improve code documentation"
                ))
            elif comment_ratio > 0.5:  # More than 50% comments
                self.smells.append(CodeSmell(
                    "high_comment_ratio", "low",
                    f"{comment_ratio:.1%} of lines are comments",
                    1,
                    "Consider if some comments are redundant or if the code needs refactoring"
                ))
    
    def _detect_todo_comments(self, content: str):
        """Detect TODO/FIXME comments"""
        todo_pattern = r'(TODO|FIXME|HACK|XXX|NOTE):\s*(.+)'
        for match in re.finditer(todo_pattern, content, re.IGNORECASE):
            line_num = content[:match.start()].count('\n') + 1
            todo_text = match.group(2).strip()
            self.smells.append(CodeSmell(
                "todo_comment", "low",
                f"TODO comment: {todo_text}",
                line_num,
                "Address the TODO comment or remove it if no longer needed"
            ))
    
    def _detect_dead_code_general(self, content: str):
        """Detect dead code patterns"""
        lines = content.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            # Look for unreachable code after return statements
            if line.startswith('return') and not line.startswith('//'):
                # Check if there's non-comment code after return
                j = i + 1
                while j < len(lines) and (lines[j].strip() == '' or lines[j].startswith('    ')):
                    if lines[j].strip() and not lines[j].strip().startswith('//'):
                        self.smells.append(CodeSmell(
                            "dead_code", "medium",
                            "Unreachable code after return statement",
                            j + 1,
                            "Remove unreachable code or restructure the logic"
                        ))
                    j += 1
    
    def _detect_duplicate_strings(self, content: str):
        """Detect duplicate string literals"""
        string_pattern = r'"[^"]{10,}"'  # Strings longer than 10 characters
        strings = re.findall(string_pattern, content)
        
        string_counts = {}
        for string in strings:
            string_counts[string] = string_counts.get(string, 0) + 1
        
        for string, count in string_counts.items():
            if count > 3:  # String appears more than 3 times
                # Find first occurrence
                first_match = re.search(re.escape(string), content)
                if first_match:
                    line_num = content[:first_match.start()].count('\n') + 1
                    self.smells.append(CodeSmell(
                        "duplicate_string", "low",
                        f"String literal appears {count} times",
                        line_num,
                        "Consider extracting the string into a named constant"
                    ))
    
    def _detect_hardcoded_values(self, content: str):
        """Detect hardcoded values that should be constants (URLs, file paths, IPs, dates, etc.)"""
        # Look for hardcoded URLs, file paths, etc.
        import re
        hardcoded_patterns = [
            (r'https?://[^\s\'"<>]+', "hardcoded_url"),
            (r'[A-Za-z]:\\\\(?:[^\s\'"]+\\\\)*[^\s\'"]+', "hardcoded_path"),
            (r'(?<!:)\/(?:[^\s\'"]+\/)*[^\s\'"]+', "hardcoded_path"),
            (r'\b\d{4}-\d{2}-\d{2}\b', "hardcoded_date"),
            (r'\b(?:\d{1,3}\.){3}\d{1,3}\b', "hardcoded_ip"),
        ]
        
        for pattern, smell_type in hardcoded_patterns:
            for match in re.finditer(pattern, content):
                line_num = content[:match.start()].count('\n') + 1
                value = match.group(0)

                # Filter out harmless paths like import statements or comments
                if re.match(r'^\s*(import|package)\b', value):
                    continue

                self.smells.append(CodeSmell(
                    smell_type, 
                    "low",
                    f"Hardcoded value detected: {value}",
                    line_num,
                    "Consider extracting this value into a named constant or configuration"
                ))
    
    def get_smell_summary(self) -> Dict[str, Any]:
        """Get a summary of detected code smells"""
        if not self.smells:
            return {
                "total_smells": 0,
                "by_severity": {"critical": 0, "high": 0, "medium": 0, "low": 0},
                "by_type": {},
                "smells": []
            }
        
        by_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        by_type = {}
        
        for smell in self.smells:
            by_severity[smell.severity] += 1
            by_type[smell.smell_type] = by_type.get(smell.smell_type, 0) + 1
        
        return {
            "total_smells": len(self.smells),
            "by_severity": by_severity,
            "by_type": by_type,
            "smells": [
                {
                    "type": smell.smell_type,
                    "severity": smell.severity,
                    "description": smell.description,
                    "line": smell.line_number,
                    "suggestion": smell.suggestion
                }
                for smell in self.smells
            ]
        }
    
    def print_smell_report(self):
        """Print a formatted report of detected code smells"""
        if not self.smells:
            print("No code smells detected!")
            return
        
        # print("\nCode Smell Analysis Report")
        # print(f"Total smells detected: {len(self.smells)}")
        
        # Group by severity
        # by_severity = {"critical": [], "high": [], "medium": [], "low": []}
        # for smell in self.smells:
        #     by_severity[smell.severity].append(smell)
        
        # # Print by severity
        # for severity, smells in by_severity.items():
        #     if smells:
        #         print(f"\n{severity.upper()} SEVERITY ({len(smells)} issues):")
        #         for smell in smells:
        #             print(f"  Line {smell.line_number}: {smell.description}")
        #             print(f"    Suggestion: {smell.suggestion}")
        #             print()
