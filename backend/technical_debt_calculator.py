"""
Technical Debt Calculation Module
Calculates technical debt metrics based on code quality, complexity, and code smells
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import math

@dataclass
class TechnicalDebtMetrics:
    """Represents technical debt metrics"""
    total_debt_score: float  # 0-100, higher = more debt
    debt_breakdown: Dict[str, float]  # Breakdown by category
    estimated_hours: float  # Estimated hours to fix
    priority_issues: List[Dict[str, Any]]  # High priority issues
    debt_trend: str  # 'increasing', 'stable', 'decreasing'
    recommendations: List[str]  # Actionable recommendations

class TechnicalDebtCalculator:
    """
    Calculates technical debt based on various code metrics
    """
    
    def __init__(self):
        # Weight factors for different debt sources
        self.weights = {
            'code_smells': 0.35,
            'complexity': 0.25,
            'maintainability': 0.20,
            'documentation': 0.10,
            'duplication': 0.10
        }
        
        # Cost multipliers (hours per issue type)
        self.cost_multipliers = {
            'critical': 8.0,
            'high': 4.0,
            'medium': 2.0,
            'low': 0.5,
            'long_function': 3.0,
            'god_class': 6.0,
            'duplicate_code': 2.5,
            'deep_nesting': 2.0,
            'complex_condition': 1.5,
            'magic_number': 0.3,
            'unused_import': 0.1,
            'missing_documentation': 1.0
        }
    
    def calculate_debt(
        self,
        quality_score: Optional[Dict[str, Any]] = None,
        code_smells: Optional[Dict[str, Any]] = None,
        ml_complexity: Optional[Dict[str, Any]] = None,
        ast_data: Optional[Dict[str, Any]] = None
    ) -> TechnicalDebtMetrics:
        """
        Calculate technical debt from various analysis results
        
        Args:
            quality_score: Quality metrics from CodeQualityAnalyzer
            code_smells: Code smells summary from CodeSmellDetector
            ml_complexity: ML complexity prediction
            ast_data: AST analysis data
        
        Returns:
            TechnicalDebtMetrics object
        """
        debt_breakdown = {}
        
        # 1. Calculate debt from code smells
        smell_debt = self._calculate_smell_debt(code_smells)
        debt_breakdown['code_smells'] = smell_debt
        
        # 2. Calculate debt from complexity
        complexity_debt = self._calculate_complexity_debt(quality_score, ml_complexity)
        debt_breakdown['complexity'] = complexity_debt
        
        # 3. Calculate debt from maintainability
        maintainability_debt = self._calculate_maintainability_debt(quality_score, code_smells)
        debt_breakdown['maintainability'] = maintainability_debt
        
        # 4. Calculate debt from documentation
        documentation_debt = self._calculate_documentation_debt(quality_score, ast_data)
        debt_breakdown['documentation'] = documentation_debt
        
        # 5. Calculate debt from code duplication
        duplication_debt = self._calculate_duplication_debt(code_smells)
        debt_breakdown['duplication'] = duplication_debt
        
        # Calculate weighted total debt score
        total_debt_score = sum(
            debt_breakdown.get(category, 0) * weight
            for category, weight in self.weights.items()
        )
        
        # Ensure score is between 0-100
        total_debt_score = max(0, min(100, total_debt_score))
        
        # Estimate hours to fix
        estimated_hours = self._estimate_fix_hours(code_smells, quality_score)
        
        # Get priority issues
        priority_issues = self._get_priority_issues(code_smells, quality_score)
        
        # Determine debt trend (simplified - would need historical data for real trend)
        debt_trend = self._determine_debt_trend(total_debt_score)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            debt_breakdown, code_smells, quality_score, total_debt_score
        )
        
        return TechnicalDebtMetrics(
            total_debt_score=round(total_debt_score, 2),
            debt_breakdown={k: round(v, 2) for k, v in debt_breakdown.items()},
            estimated_hours=round(estimated_hours, 1),
            priority_issues=priority_issues,
            debt_trend=debt_trend,
            recommendations=recommendations
        )
    
    def _calculate_smell_debt(self, code_smells: Optional[Dict[str, Any]]) -> float:
        """Calculate debt from code smells"""
        if not code_smells or code_smells.get('total_smells', 0) == 0:
            return 0.0
        
        by_severity = code_smells.get('by_severity', {})
        by_type = code_smells.get('by_type', {})
        
        # Calculate debt based on severity
        severity_scores = {
            'critical': 25.0,
            'high': 15.0,
            'medium': 8.0,
            'low': 3.0
        }
        
        debt = 0.0
        for severity, count in by_severity.items():
            debt += count * severity_scores.get(severity, 0)
        
        # Add type-specific penalties
        type_penalties = {
            'god_class': 20.0,
            'long_function': 12.0,
            'duplicate_code': 10.0,
            'deep_nesting': 8.0,
            'complex_condition': 5.0
        }
        
        for smell_type, count in by_type.items():
            debt += count * type_penalties.get(smell_type, 2.0)
        
        # Normalize to 0-100 scale (assuming max reasonable debt)
        max_reasonable_debt = 200.0
        normalized_debt = min(100.0, (debt / max_reasonable_debt) * 100)
        
        return normalized_debt
    
    def _calculate_complexity_debt(
        self,
        quality_score: Optional[Dict[str, Any]],
        ml_complexity: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate debt from code complexity"""
        debt = 0.0
        
        # From quality score complexity (inverted - lower score = higher debt)
        if quality_score:
            complexity_score = quality_score.get('complexity', 100)
            # Invert: complexity score of 50 means 50 debt
            debt += (100 - complexity_score) * 0.6
        
        # From ML complexity prediction
        if ml_complexity and ml_complexity.get('prediction'):
            prediction = ml_complexity['prediction']
            if not prediction.get('error'):
                complexity_desc = prediction.get('complexity_description', '')
                
                # Map complexity to debt
                complexity_debt_map = {
                    'O(1)': 0.0,
                    'O(log n)': 10.0,
                    'O(n)': 25.0,
                    'O(n log n)': 40.0,
                    'O(n²)': 60.0
                }
                
                base_debt = complexity_debt_map.get(complexity_desc, 30.0)
                
                # Adjust based on confidence (lower confidence = more uncertainty = more debt)
                confidence = prediction.get('confidence', 1.0)
                adjusted_debt = base_debt * (1.0 + (1.0 - confidence))
                
                debt += adjusted_debt * 0.4
        
        return min(100.0, debt)
    
    def _calculate_maintainability_debt(
        self,
        quality_score: Optional[Dict[str, Any]],
        code_smells: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate debt from maintainability issues"""
        debt = 0.0
        
        if quality_score:
            maintainability_score = quality_score.get('maintainability', 100)
            # Invert: lower maintainability = higher debt
            debt += (100 - maintainability_score) * 0.7
        
        # Add debt from maintainability-related smells
        if code_smells:
            by_type = code_smells.get('by_type', {})
            maintainability_smells = ['god_class', 'long_function', 'duplicate_code']
            
            for smell_type in maintainability_smells:
                count = by_type.get(smell_type, 0)
                debt += count * 5.0
        
        return min(100.0, debt)
    
    def _calculate_documentation_debt(
        self,
        quality_score: Optional[Dict[str, Any]],
        ast_data: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate debt from missing or poor documentation"""
        debt = 0.0
        
        if quality_score:
            doc_score = quality_score.get('documentation', 100)
            # Invert: lower documentation score = higher debt
            debt += (100 - doc_score) * 0.8
        
        # Add debt based on code structure vs documentation ratio
        if ast_data:
            functions = len(ast_data.get('functions', []))
            classes = len(ast_data.get('classes', []))
            total_elements = functions + classes
            
            # Estimate documentation debt (simplified)
            if total_elements > 0:
                # Assume each function/class should have documentation
                # Missing docs = debt
                estimated_missing_docs = max(0, total_elements * 0.3)  # Assume 30% missing
                debt += estimated_missing_docs * 2.0
        
        return min(100.0, debt)
    
    def _calculate_duplication_debt(self, code_smells: Optional[Dict[str, Any]]) -> float:
        """Calculate debt from code duplication"""
        debt = 0.0
        
        if code_smells:
            by_type = code_smells.get('by_type', {})
            duplicate_count = by_type.get('duplicate_code', 0)
            
            # Each duplicate instance adds debt
            debt += duplicate_count * 8.0
            
            # Check for duplicate strings
            duplicate_strings = by_type.get('duplicate_string', 0)
            debt += duplicate_strings * 1.0
        
        return min(100.0, debt)
    
    def _estimate_fix_hours(
        self,
        code_smells: Optional[Dict[str, Any]],
        quality_score: Optional[Dict[str, Any]]
    ) -> float:
        """Estimate hours needed to fix all issues (lenient calculation)"""
        total_hours = 0.0
        
        if code_smells:
            smells_list = code_smells.get('smells', [])
            
            for smell in smells_list:
                severity = smell.get('severity', 'low')
                smell_type = smell.get('type', '')
                
                # Use the smaller of severity or type cost (not multiply)
                severity_hours = self.cost_multipliers.get(severity, 0.25)
                type_hours = self.cost_multipliers.get(smell_type, 0.25)
                
                # Take the average instead of multiplying (more lenient)
                total_hours += (severity_hours + type_hours) / 2
        
        # Add minimal hours for quality improvements (very lenient)
        if quality_score:
            issues = quality_score.get('issues', [])
            # Only 0.25 hour per issue for general improvements
            total_hours += len(issues) * 0.25
        
        # Cap total hours based on reasonable expectations
        # Small file (<100 lines): max 2 hours
        # Medium file (<500 lines): max 4 hours  
        # Large file: max 8 hours
        total_hours = min(total_hours, 8.0)
        
        return total_hours
    
    def _get_priority_issues(
        self,
        code_smells: Optional[Dict[str, Any]],
        quality_score: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Get high priority issues that need immediate attention"""
        priority_issues = []
        
        if code_smells:
            smells_list = code_smells.get('smells', [])
            
            # Get critical and high severity issues
            for smell in smells_list:
                severity = smell.get('severity', 'low')
                if severity in ['critical', 'high']:
                    priority_issues.append({
                        'type': smell.get('type', 'unknown'),
                        'severity': severity,
                        'description': smell.get('description', ''),
                        'line': smell.get('line', 0),
                        'suggestion': smell.get('suggestion', '')
                    })
        
        # Add quality score issues
        if quality_score:
            issues = quality_score.get('issues', [])
            for issue in issues[:5]:  # Top 5 issues
                if 'Critical' in issue or 'High' in issue:
                    priority_issues.append({
                        'type': 'quality_issue',
                        'severity': 'high',
                        'description': issue,
                        'line': 0,
                        'suggestion': 'Review and address quality issues'
                    })
        
        # Sort by severity (critical first)
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        priority_issues.sort(key=lambda x: severity_order.get(x.get('severity', 'low'), 3))
        
        return priority_issues[:10]  # Top 10 priority issues
    
    def _determine_debt_trend(self, current_debt: float) -> str:
        """
        Determine debt trend (simplified - would need historical data)
        For now, categorize based on current debt level
        """
        if current_debt >= 70:
            return 'increasing'  # High debt likely increasing
        elif current_debt >= 40:
            return 'stable'  # Moderate debt
        else:
            return 'decreasing'  # Low debt
    
    def _generate_recommendations(
        self,
        debt_breakdown: Dict[str, float],
        code_smells: Optional[Dict[str, Any]],
        quality_score: Optional[Dict[str, Any]],
        total_debt: float
    ) -> List[str]:
        """Generate actionable recommendations to reduce technical debt"""
        recommendations = []
        
        # High-level recommendations based on total debt
        if total_debt >= 70:
            recommendations.append("🚨 CRITICAL: High technical debt detected. Prioritize refactoring immediately.")
        elif total_debt >= 50:
            recommendations.append("⚠️ WARNING: Moderate technical debt. Plan refactoring sprints.")
        elif total_debt >= 30:
            recommendations.append("ℹ️ INFO: Some technical debt present. Address incrementally.")
        
        # Category-specific recommendations
        if debt_breakdown.get('code_smells', 0) > 40:
            recommendations.append("Focus on eliminating code smells, especially critical and high-severity issues.")
        
        if debt_breakdown.get('complexity', 0) > 40:
            recommendations.append("Reduce code complexity by breaking down large functions and simplifying logic.")
        
        if debt_breakdown.get('maintainability', 0) > 40:
            recommendations.append("Improve maintainability by refactoring god classes and long functions.")
        
        if debt_breakdown.get('documentation', 0) > 40:
            recommendations.append("Add comprehensive documentation to improve code understanding.")
        
        if debt_breakdown.get('duplication', 0) > 30:
            recommendations.append("Eliminate code duplication by extracting common functionality.")
        
        # Specific recommendations from quality score
        if quality_score:
            quality_recommendations = quality_score.get('recommendations', [])
            recommendations.extend(quality_recommendations[:3])  # Top 3
        
        # If no specific recommendations, add general ones
        if len(recommendations) == 0:
            recommendations.append("Code quality is good! Maintain current standards.")
        
        return recommendations[:8]  # Limit to 8 recommendations
    
    def get_debt_summary(self, metrics: TechnicalDebtMetrics) -> Dict[str, Any]:
        """Get a summary dictionary of technical debt metrics"""
        return {
            'total_debt_score': metrics.total_debt_score,
            'debt_level': self._get_debt_level(metrics.total_debt_score),
            'debt_breakdown': metrics.debt_breakdown,
            'estimated_hours': metrics.estimated_hours,
            'priority_issues_count': len(metrics.priority_issues),
            'debt_trend': metrics.debt_trend,
            'recommendations_count': len(metrics.recommendations),
            'priority_issues': metrics.priority_issues[:5],  # Top 5
            'recommendations': metrics.recommendations
        }
    
    def _get_debt_level(self, score: float) -> str:
        """Get debt level category"""
        if score >= 70:
            return 'critical'
        elif score >= 50:
            return 'high'
        elif score >= 30:
            return 'medium'
        else:
            return 'low'
