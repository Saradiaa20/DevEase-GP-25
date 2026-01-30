"""
Code Quality Metrics and Scoring System
Provides comprehensive code quality analysis and scoring
"""

from typing import Dict, Any, List
from dataclasses import dataclass
import os
import re

@dataclass
class QualityScore:
    """Represents a code quality score with breakdown"""
    overall_score: float  # 0-100
    maintainability: float
    readability: float
    complexity: float
    documentation: float
    issues: List[str]
    recommendations: List[str]

class CodeQualityAnalyzer:
    """Analyzes code quality and provides scoring"""
    
    def __init__(self):
        self.file_path = ""
        self.content = ""
        self.lines = []
        self.total_lines = 0
    
    def analyze_file(self, file_path: str, smell_summary: Dict[str, Any]) -> QualityScore:
        """Analyze a file and return quality score"""
        self.file_path = file_path
        
        with open(file_path, 'r', encoding='utf-8') as file:
            self.content = file.read()
            self.lines = self.content.splitlines()
            self.total_lines = len(self.lines)
        
        # Calculate individual scores
        maintainability_score = self._calculate_maintainability_score(smell_summary)
        readability_score = self._calculate_readability_score()
        complexity_score = self._calculate_complexity_score()
        documentation_score = self._calculate_documentation_score()
        
        # Calculate overall score (weighted average)
        overall_score = (
            maintainability_score * 0.3 +
            readability_score * 0.25 +
            complexity_score * 0.25 +
            documentation_score * 0.2
        )
        
        # Generate issues and recommendations
        issues = self._generate_issues(smell_summary)
        recommendations = self._generate_recommendations(smell_summary, issues)
        
        return QualityScore(
            overall_score=round(overall_score, 1),
            maintainability=round(maintainability_score, 1),
            readability=round(readability_score, 1),
            complexity=round(complexity_score, 1),
            documentation=round(documentation_score, 1),
            issues=issues,
            recommendations=recommendations
        )
    
    def _calculate_maintainability_score(self, smell_summary: Dict[str, Any]) -> float:
        """Calculate maintainability score based on code smells"""
        base_score = 100.0
        
        # Penalize based on smell severity
        # by_severity = smell_summary.get("by_severity", {})
        # base_score -= by_severity.get("critical", 0) * 15  # -15 points per critical smell
        # base_score -= by_severity.get("high", 0) * 10      # -10 points per high severity smell
        # base_score -= by_severity.get("medium", 0) * 5     # -5 points per medium severity smell
        # base_score -= by_severity.get("low", 0) * 2        # -2 points per low severity smell
        
        # Penalize for specific maintainability issues
        by_type = smell_summary.get("by_type", {})
        base_score -= by_type.get("duplicate_code", 0) * 8
        base_score -= by_type.get("long_function", 0) * 6
        base_score -= by_type.get("god_class", 0) * 12
        base_score -= by_type.get("dead_code", 0) * 4
        
        return max(0, min(100, base_score))
    
    def _calculate_readability_score(self) -> float:
        """Calculate readability score based on code structure"""
        base_score = 100.0
        
        # Check line length (only penalize if significant portion of lines are too long)
        long_lines = sum(1 for line in self.lines if len(line) > 120)
        if long_lines > 0 and self.total_lines > 0:
            long_line_ratio = long_lines / self.total_lines
            # Only penalize up to 15 points for long lines
            base_score -= min(15, long_line_ratio * 30)
        
        # Check for consistent indentation (minor penalty)
        indentation_issues = self._check_indentation_consistency()
        base_score -= min(10, indentation_issues * 5)
        
        # Check for meaningful variable names (capped penalty)
        naming_issues = self._check_naming_conventions()
        # Cap at 15 points max - some single-letter vars are acceptable
        base_score -= min(15, naming_issues * 1.5)
        
        # Check for proper spacing (capped penalty)
        spacing_issues = self._check_spacing_issues()
        # Cap at 10 points max - minor style issues shouldn't tank the score
        base_score -= min(10, spacing_issues * 0.5)
        
        return max(0, min(100, base_score))
    
    def _calculate_complexity_score(self) -> float:
        """Calculate complexity score (inverted - lower complexity = higher score)"""
        base_score = 100.0
        
        # Check cyclomatic complexity indicators
        complexity_indicators = 0
        for line in self.lines:
            line = line.strip()
            # Count complexity indicators
            complexity_indicators += line.count('if ')
            complexity_indicators += line.count('elif ')
            complexity_indicators += line.count('else:')
            complexity_indicators += line.count('for ')
            complexity_indicators += line.count('while ')
            complexity_indicators += line.count('&&')
            complexity_indicators += line.count('||')
            complexity_indicators += line.count('and ')
            complexity_indicators += line.count('or ')
        
        # Normalize by file size
        if self.total_lines > 0:
            complexity_ratio = complexity_indicators / self.total_lines
            base_score -= complexity_ratio * 50
        
        # Check for deeply nested structures
        max_nesting = self._calculate_max_nesting()
        if max_nesting > 4:
            base_score -= (max_nesting - 4) * 10
        
        return max(0, min(100, base_score))
    
    def _calculate_documentation_score(self) -> float:
        """Calculate documentation score"""
        if self.total_lines == 0:
            return 0
        
        comment_lines = 0
        in_multiline_docstring = False
        docstring_delimiter = None
        
        for line in self.lines:
            stripped = line.strip()
            
            # Handle multi-line docstrings (Python)
            if not in_multiline_docstring:
                # Check for start of docstring
                if '"""' in stripped or "'''" in stripped:
                    delimiter = '"""' if '"""' in stripped else "'''"
                    # Count occurrences to determine if it's single-line or multi-line
                    count = stripped.count(delimiter)
                    if count == 1:
                        # Start of multi-line docstring
                        in_multiline_docstring = True
                        docstring_delimiter = delimiter
                        comment_lines += 1
                    elif count >= 2:
                        # Single-line docstring (opening and closing on same line)
                        comment_lines += 1
                # Check for regular comments
                elif stripped.startswith('#') or stripped.startswith('//'):
                    comment_lines += 1
                # Check for block comments (Java/JS style)
                elif stripped.startswith('/*'):
                    comment_lines += 1
                elif stripped.startswith('*') and not stripped.startswith('*/'):
                    # Middle of a block comment
                    comment_lines += 1
            else:
                # Inside a multi-line docstring - count all lines
                comment_lines += 1
                # Check for end of docstring
                if docstring_delimiter in stripped:
                    in_multiline_docstring = False
                    docstring_delimiter = None
        
        # Calculate comment ratio
        comment_ratio = comment_lines / self.total_lines
        
        # Score based on comment ratio (more lenient thresholds)
        if comment_ratio >= 0.20:  # 20% or more comments/docs
            return 100
        elif comment_ratio >= 0.15:  # 15-20% comments
            return 90
        elif comment_ratio >= 0.10:  # 10-15% comments
            return 80
        elif comment_ratio >= 0.05:  # 5-10% comments
            return 60
        elif comment_ratio >= 0.02:  # 2-5% comments
            return 40
        else:  # Less than 2% comments
            return 20
    
    def _check_indentation_consistency(self) -> int:
        """Check for indentation consistency issues"""
        issues = 0
        indentations = []
        
        for line in self.lines:
            if line.strip():  # Skip empty lines
                leading_spaces = len(line) - len(line.lstrip())
                if leading_spaces > 0:
                    indentations.append(leading_spaces)
        
        if indentations:
            # Check for mixed tabs and spaces
            has_tabs = any('\t' in line for line in self.lines if line.strip())
            has_spaces = any(line.startswith(' ') for line in self.lines if line.strip())
            
            if has_tabs and has_spaces:
                issues += 1
            
            # Check for inconsistent indentation levels
            unique_indents = set(indentations)
            if len(unique_indents) > 5:  # Too many different indentation levels
                issues += 1
        
        return issues
    
    def _check_naming_conventions(self) -> int:
        """Check for naming convention issues"""
        issues = 0
        
        # Look for single letter variables (except in loops)
        for i, line in enumerate(self.lines):
            if '=' in line and not line.strip().startswith('#'):
                # Simple check for single letter variables
                if re.search(r'\b[a-z]\s*=', line):
                    # Check if it's in a for loop
                    if not any('for ' in prev_line for prev_line in self.lines[max(0, i-2):i+1]):
                        issues += 1
        
        return issues
    
    def _check_spacing_issues(self) -> int:
        """Check for spacing issues"""
        issues = 0
        
        for line in self.lines:
            # Check for missing spaces around operators
            if re.search(r'[a-zA-Z0-9][=+\-*/][a-zA-Z0-9]', line):
                issues += 1
            
            # Check for multiple consecutive spaces
            if '  ' in line and not line.strip().startswith('#'):
                issues += 1
        
        return issues
    
    def _calculate_max_nesting(self) -> int:
        """Calculate maximum nesting level in the file"""
        max_nesting = 0
        current_nesting = 0
        
        for line in self.lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                # Count opening braces/brackets
                current_nesting += line.count('{') + line.count('[') + line.count('(')
                # Count closing braces/brackets
                current_nesting -= line.count('}') + line.count(']') + line.count(')')
                
                # Track maximum nesting
                max_nesting = max(max_nesting, current_nesting)
        
        return max_nesting
    
    def _count_documentation_lines(self) -> int:
        """Count all documentation lines including multi-line docstrings"""
        comment_lines = 0
        in_multiline_docstring = False
        docstring_delimiter = None
        
        for line in self.lines:
            stripped = line.strip()
            
            # Handle multi-line docstrings (Python)
            if not in_multiline_docstring:
                if '"""' in stripped or "'''" in stripped:
                    delimiter = '"""' if '"""' in stripped else "'''"
                    count = stripped.count(delimiter)
                    if count == 1:
                        in_multiline_docstring = True
                        docstring_delimiter = delimiter
                        comment_lines += 1
                    elif count >= 2:
                        comment_lines += 1
                elif stripped.startswith('#') or stripped.startswith('//'):
                    comment_lines += 1
                elif stripped.startswith('/*'):
                    comment_lines += 1
                elif stripped.startswith('*') and not stripped.startswith('*/'):
                    comment_lines += 1
            else:
                comment_lines += 1
                if docstring_delimiter in stripped:
                    in_multiline_docstring = False
                    docstring_delimiter = None
        
        return comment_lines
    
    def _generate_issues(self, smell_summary: Dict[str, Any]) -> List[str]:
        """Generate list of issues based on analysis"""
        issues = []
        
        by_severity = smell_summary.get("by_severity", {})
        by_type = smell_summary.get("by_type", {})
        
        if by_severity.get("critical", 0) > 0:
            issues.append(f"Critical issues found: {by_severity['critical']} critical code smells")
        
        if by_severity.get("high", 0) > 0:
            issues.append(f"High priority issues: {by_severity['high']} high severity code smells")
        
        if by_type.get("duplicate_code", 0) > 0:
            issues.append(f"Code duplication: {by_type['duplicate_code']} instances of duplicate code")
        
        if by_type.get("long_function", 0) > 0:
            issues.append(f"Long functions: {by_type['long_function']} functions are too long")
        
        if by_type.get("god_class", 0) > 0:
            issues.append(f"God classes: {by_type['god_class']} classes are too large")
        
        # Check file size
        if self.total_lines > 1000:
            issues.append(f"Large file: {self.total_lines} lines (consider splitting)")
        elif self.total_lines > 500:
            issues.append(f"Moderately large file: {self.total_lines} lines")
        
        # Check comment ratio (including docstrings)
        comment_lines = self._count_documentation_lines()
        comment_ratio = comment_lines / self.total_lines if self.total_lines > 0 else 0
        
        # Only warn if documentation is very low (less than 2%)
        if comment_ratio < 0.02:
            issues.append("Very low documentation: Less than 2% of lines are comments or docstrings")
        elif comment_ratio > 0.5:
            issues.append("Excessive comments: More than 50% of lines are comments")
        
        return issues
    
    def _generate_recommendations(self, smell_summary: Dict[str, Any], issues: List[str]) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        by_type = smell_summary.get("by_type", {})
        
        if by_type.get("duplicate_code", 0) > 0:
            recommendations.append("Extract common functionality into shared functions/methods")
        
        if by_type.get("long_function", 0) > 0:
            recommendations.append("Break down long functions into smaller, focused functions")
        
        if by_type.get("god_class", 0) > 0:
            recommendations.append("Split large classes into smaller, single-responsibility classes")
        
        if by_type.get("complex_condition", 0) > 0:
            recommendations.append("Simplify complex conditions by extracting them into well-named methods")
        
        if by_type.get("magic_number", 0) > 0:
            recommendations.append("Replace magic numbers with named constants")
        
        if by_type.get("unused_import", 0) > 0:
            recommendations.append("Remove unused imports to clean up the code")
        
        # File size recommendations
        if self.total_lines > 500:
            recommendations.append("Consider splitting this file into smaller, more focused files")
        
        # Documentation recommendations (using proper counting including docstrings)
        comment_lines = self._count_documentation_lines()
        comment_ratio = comment_lines / self.total_lines if self.total_lines > 0 else 0
        
        # Only recommend more comments if very low documentation
        if comment_ratio < 0.02:
            recommendations.append("Add more comments to improve code documentation")
        elif comment_ratio > 0.5:
            recommendations.append("Review comments - some may be redundant or the code needs refactoring")
        
        # General recommendations
        if not recommendations:
            recommendations.append("Code quality is good! Keep up the good work!")
        else:
            recommendations.append("Focus on addressing the highest priority issues first")
        
        return recommendations
    
    def print_quality_report(self, quality_score: QualityScore):
        """Print a formatted quality report"""
        # print("\nCode Quality Analysis Report")
        # print("-" * 60)
        
        # Overall score
        if quality_score.overall_score >= 90:
            score_text = "Excellent"
        elif quality_score.overall_score >= 80:
            score_text = "Good"
        elif quality_score.overall_score >= 70:
            score_text = "Fair"
        else:
            score_text = "Needs Improvement"
        
        print(f"Overall Quality Score: {quality_score.overall_score}/100 ({score_text})")
        print()
        
        # Detailed scores
        print("Detailed Scores:")
        print(f"  Maintainability: {quality_score.maintainability}/100")
        print(f"  Readability: {quality_score.readability}/100")
        print(f"  Complexity: {quality_score.complexity}/100")
        print(f"  Documentation: {quality_score.documentation}/100")
        print()
        
        # Issues
        if quality_score.issues:
            print("Issues Found:")
            for i, issue in enumerate(quality_score.issues, 1):
                print(f"  {i}. {issue}")
            print()
        
        # Recommendations
        if quality_score.recommendations:
            print("Recommendations:")
            for i, rec in enumerate(quality_score.recommendations, 1):
                print(f"  {i}. {rec}")
            print()
        
        # Quality level summary
        print("Quality Level Summary:")
        if quality_score.overall_score >= 90:
            print("  Your code demonstrates excellent quality with minimal issues!")
        elif quality_score.overall_score >= 80:
            print("  Your code is in good shape with room for minor improvements.")
        elif quality_score.overall_score >= 70:
            print("  Your code has some quality issues that should be addressed.")
        else:
            print("  Your code needs significant improvements to meet quality standards.")
