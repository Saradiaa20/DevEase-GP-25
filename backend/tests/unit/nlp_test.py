import os
import json
import pytest
from unittest.mock import patch, MagicMock
import requests

# Import the module components to test
from app.services.nlp_explainer import (
    generate_nlp_report,
    _extract_json,
    _plural,
    _score_label,
    _build_full_report,
    _fallback_report
)

class TestNLPHelpers:
    
    def test_plural(self):
        """Test singular and plural word generation."""
        assert _plural(1, "smell") == "smell"
        assert _plural(2, "smell") == "smells"
        assert _plural(1, "class", "classes") == "class"
        assert _plural(3, "class", "classes") == "classes"

    def test_score_label(self):
        """Test the quality score to label mapping."""
        assert _score_label(90) == "excellent"
        assert _score_label(75) == "good"
        assert _score_label(60) == "fair"
        assert _score_label(45) == "poor"
        assert _score_label(20) == "very poor"

    def test_extract_json_clean(self):
        """Test extracting standard JSON strings."""
        data = '{"summary": "test"}'
        assert _extract_json(data) == {"summary": "test"}

    def test_extract_json_markdown_fences(self):
        """Test extracting JSON wrapped in markdown code blocks."""