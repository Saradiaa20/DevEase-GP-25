import os 

from app.services.technical_debt_calculator import TechnicalDebtCalculator

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

def load_file(relative_path):
    full_path = os.path.join(BASE_DIR, relative_path)
    with open(full_path, "r", encoding="utf-8") as f:
        return f.read()
    

#Test Case 1 
def test_python_high_technical_debt():
    calc = TechnicalDebtCalculator()

    code_smells = {
        "by_severity": {
            "critical": 2,
            "high": 4,
            "medium": 6,
            "low": 5
        },
        "by_type": {
            "long_function": 2,
            "deep_nesting": 2,
            "duplicate_code": 1,
            "complex_condition": 2,
            "magic_number": 3
        },
        "smells": [
            {"type": "long_function", "severity": "high", "description": "", "line": 10, "suggestion": ""},
            {"type": "deep_nesting", "severity": "high", "description": "", "line": 20, "suggestion": ""},
        ]
    }

    quality_score = {
        "complexity": 40,
        "maintainability": 45,
        "documentation": 20,
        "issues": ["High complexity detected", "Critical structure issue"],
        "recommendations": ["Refactor functions", "Improve structure"]
    }

    ml_complexity = {
        "prediction": {
            "complexity_description": "O(n²)",
            "confidence": 0.9
        }
    }

    ast_data = {
        "functions": list(range(10)),
        "classes": []
    }

    metrics = calc.calculate_debt(
        quality_score=quality_score,
        code_smells=code_smells,
        ml_complexity=ml_complexity,
        ast_data=ast_data
    )

    # ✅ Assertions
    assert metrics.total_debt_score > 50
    assert metrics.debt_severity in ["high", "critical"]
    assert metrics.estimated_hours >= 7.0   
    assert len(metrics.priority_issues) > 0

#Test Case 2
def test_python_debt_summary():
    calc = TechnicalDebtCalculator()

    fake_metrics = calc.calculate_debt(
        quality_score={"complexity": 50, "maintainability": 50, "documentation": 50},
        code_smells={
            "by_severity": {"high": 3},
            "by_type": {"long_function": 2},
            "smells": [{"type": "long_function", "severity": "high"}]
        }
    )

    summary = calc.get_debt_summary(fake_metrics)

    assert "total_debt_score" in summary
    assert "debt_level" in summary
    assert summary["priority_issues_count"] >= 0

#Test Case 3
def test_java_moderate_technical_debt():
    calc = TechnicalDebtCalculator()

    code_smells = {
        "by_severity": {
            "high": 2,
            "medium": 3,
            "low": 2
        },
        "by_type": {
            "god_class": 1,
            "long_method": 2
        },
        "smells": [
            {"type": "god_class", "severity": "high", "description": "", "line": 5, "suggestion": ""}
        ]
    }

    quality_score = {
        "complexity": 60,
        "maintainability": 55,
        "documentation": 40,
        "issues": [],
        "recommendations": []
    }

    ml_complexity = {
        "prediction": {
            "complexity_description": "O(n log n)",
            "confidence": 0.8
        }
    }

    metrics = calc.calculate_debt(
        quality_score=quality_score,
        code_smells=code_smells,
        ml_complexity=ml_complexity
    )

    assert 30 <= metrics.total_debt_score <= 80
    assert metrics.debt_severity in ["medium", "high"]

#Test Case 4
def test_low_technical_debt():
    calc = TechnicalDebtCalculator()

    metrics = calc.calculate_debt(
        quality_score={
            "complexity": 90,
            "maintainability": 90,
            "documentation": 90,
            "issues": []
        },
        code_smells={
            "by_severity": {},
            "by_type": {},
            "smells": []
        },
        ml_complexity={
            "prediction": {
                "complexity_description": "O(1)",
                "confidence": 1.0
            }
        }
    )

    assert metrics.total_debt_score < 30
    assert metrics.debt_severity == "low"