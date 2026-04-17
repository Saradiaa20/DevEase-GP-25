
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import joblib
import numpy as np
import pandas as pd

from app.ml.dp_tabular_features import FEATURE_COLUMN_ORDER, extract_tabular_features

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BACKEND_DIR, "ml", "models", "design_pattern_models")


PATTERN_CATEGORY: Dict[str, str] = {
    "Singleton": "Creational",
    "Factory": "Creational",
    "Builder": "Creational",
    "Prototype": "Creational",
    "Adapter": "Structural",
    "Decorator": "Structural",
    "Facade": "Structural",
    "Proxy": "Structural",
    "Strategy": "Behavioral",
    "Observer": "Behavioral",
    "Command": "Behavioral",
    "State": "Behavioral",
}

PATTERN_DESCRIPTIONS: Dict[str, str] = {
    "Singleton": "Ensures a class has only one instance.",
    "Factory": "Creates objects without specifying exact class.",
    "Builder": "Separates construction from representation.",
    "Prototype": "Creates objects by cloning.",
    "Adapter": "Converts interface.",
    "Decorator": "Adds behavior dynamically.",
    "Facade": "Simplifies subsystem.",
    "Proxy": "Acts as placeholder.",
    "Strategy": "Interchangeable algorithms.",
    "Observer": "One-to-many dependency.",
    "Command": "Encapsulates request.",
    "State": "Changes behavior with state.",
}


class DesignPatternDetector:
    def __init__(self, model_dir: Optional[str] = None):
        self.model_dir = model_dir or MODEL_DIR
        self._pipe = None
        self._label_encoder = None
        self._feature_columns: Optional[List[str]] = None
        self._model_loaded = False

    def load_model(self) -> bool:
        try:
            self._pipe = joblib.load(os.path.join(self.model_dir, "best_model.pkl"))
            self._label_encoder = joblib.load(os.path.join(self.model_dir, "label_encoder.pkl"))
            self._feature_columns = joblib.load(os.path.join(self.model_dir, "feature_columns.pkl"))
            self._model_loaded = True
            return True
        except:
            return False

    def _build_dataframe(self, features: Dict[str, Any]) -> pd.DataFrame:
        cols = self._feature_columns or FEATURE_COLUMN_ORDER
        row = {c: features.get(c, 0) for c in cols}
        return pd.DataFrame([row], columns=cols)

    @staticmethod
    def _is_none_label(label: str) -> bool:
        return str(label).strip().lower() == "none"

    def _predict_ml(self, code_content: str, language: str) -> Dict[str, Any]:

        no_pattern_response = {
            "predicted_category": "None",
            "confidence": 0.0,
            "category_scores": {},
            "detected_patterns": [],
            "suggested_pattern": {
                "name": "None",
                "category": "None",
                "confidence": 0.0,
                "description": "No design pattern detected",
                "reason": "Simple or unclear structure"
            },
        }

        feats = extract_tabular_features(code_content, language)

        if str(language).lower() not in ("python", "java"):
            return {**no_pattern_response, "features": feats}

        if feats["total_methods"] == 0:
            return {**no_pattern_response, "features": feats}
    
        X = self._build_dataframe(feats)

        proba = None
        if hasattr(self._pipe, "predict_proba"):
            proba = self._pipe.predict_proba(X)[0]

        if proba is not None:
            max_conf = float(max(proba))
            if max_conf < 0.3:
                return {
                    **no_pattern_response,
                    "confidence": round(max_conf, 3),
                    "features": feats,
                }

        pred_idx = self._pipe.predict(X)[0]
        pattern_name = str(self._label_encoder.inverse_transform([pred_idx])[0])
        selected_confidence = 1.0

        if pattern_name == "Prototype" and "clone(" not in code_content:
            return {**no_pattern_response, "features": feats}

        classes = self._label_encoder.classes_

        if proba is not None:
            order = np.argsort(proba)[::-1]
            top = [(str(classes[i]), float(proba[i])) for i in order[:5]]
            selected_confidence = float(proba[pred_idx])
        else:
            top = [(pattern_name, 1.0)]
        if self._is_none_label(pattern_name):
            if proba is None or max(proba) < 0.4:
                return {**no_pattern_response, "features": feats}

            non_none_idx = [i for i, cls in enumerate(classes) if not self._is_none_label(cls)]
            if not non_none_idx:
                return {**no_pattern_response, "features": feats}

            best_idx = max(non_none_idx, key=lambda i: float(proba[i]))
            pattern_name = str(classes[best_idx])
            selected_confidence = float(proba[best_idx])
        category_scores = {"Creational": 0, "Structural": 0, "Behavioral": 0}

        if proba is not None:
            for i, cls in enumerate(classes):
                if self._is_none_label(cls):
                    continue
                cat = PATTERN_CATEGORY.get(cls, "Behavioral")
                category_scores[cat] += float(proba[i])

        predicted_category = PATTERN_CATEGORY.get(pattern_name, "Behavioral")

        return {
            "predicted_category": predicted_category,
            "confidence": round(selected_confidence, 3),
            "category_scores": category_scores,
            "detected_patterns": [],
            "suggested_pattern": {
                "name": pattern_name,
                "category": predicted_category,
                "confidence": round(selected_confidence, 3),
                "description": PATTERN_DESCRIPTIONS.get(pattern_name, ""),
            },
            "features": feats,
        }

    def get_pattern_summary(self, code_content: str, language: str = "java") -> Dict[str, Any]:
        if self._model_loaded:
            prediction = self._predict_ml(code_content, language)
        else:
            prediction = {
                "predicted_category": "Unknown",
                "confidence": 0,
                "category_scores": {},
                "detected_patterns": [],
                "suggested_pattern": {"name": "Unknown"},
                "features": {},
            }

        return {"design_patterns": prediction}