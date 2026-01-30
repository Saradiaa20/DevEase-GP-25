"""
Design Pattern Detection with Deep Learning
Detects design patterns (Creational, Structural, Behavioral) from Java code using CK metrics
"""

import os
import glob
import re
import tempfile
import zipfile
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib
import requests

# Try to import TensorFlow, fall back to sklearn if not available
try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential, load_model
    from tensorflow.keras.layers import Dense, Dropout
    from tensorflow.keras.utils import to_categorical
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.neural_network import MLPClassifier


class DesignPatternDetector:
    """
    Deep Learning based Design Pattern Detector
    Analyzes code structure to identify design patterns
    """
    
    # Design pattern categories
    CREATIONAL = ['Abstract_factory', 'Builder', 'Factory', 'Prototype', 'Singleton']
    STRUCTURAL = ['Adapter', 'Bridge', 'Composite', 'Decorator', 'Facade', 'Flyweight', 'Proxy']
    BEHAVIORAL = ['Chain_of_responsibility', 'Command', 'Interpreter', 'Iterator', 
                  'Mediator', 'Memento', 'Observer', 'State', 'Strategy', 'Template', 'Visitor']
    
    # Dataset URL (Dropbox direct download link)
    DATASET_URL = "https://www.dropbox.com/scl/fi/rfpkpzishrr944ym043gh/Dp_data.zip?rlkey=7v0cy3p1xhr2cdhpgkzjzf05f&st=jduli9hs&dl=1"
    
    # CK Metrics features used by the model
    CK_FEATURES = [
        'cbo', 'cboModified', 'fanin', 'fanout', 'wmc', 'dit', 'noc', 'rfc',
        'lcom', 'lcom*', 'tcc', 'lcc', 'totalMethodsQty', 'staticMethodsQty',
        'publicMethodsQty', 'privateMethodsQty', 'protectedMethodsQty',
        'defaultMethodsQty', 'visibleMethodsQty', 'abstractMethodsQty',
        'finalMethodsQty', 'synchronizedMethodsQty', 'totalFieldsQty',
        'staticFieldsQty', 'publicFieldsQty', 'privateFieldsQty',
        'protectedFieldsQty', 'defaultFieldsQty', 'finalFieldsQty',
        'synchronizedFieldsQty', 'nosi', 'loc', 'returnQty', 'loopQty',
        'comparisonsQty', 'tryCatchQty', 'parenthesizedExpsQty',
        'stringLiteralsQty', 'numbersQty', 'assignmentsQty', 'mathOperationsQty',
        'variablesQty', 'maxNestedBlocksQty', 'anonymousClassesQty',
        'innerClassesQty', 'lambdasQty', 'uniqueWordsQty', 'modifiers',
        'logStatementsQty'
    ]
    
    def __init__(self, model_path: str = None):
        if model_path is None:
            model_path = os.path.join(os.path.dirname(__file__), "design_pattern_model")
        self.model_path = model_path
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self._model_loaded = False
        
        # Feature columns from method.csv (28 columns after dropping file, class, method)
        self.feature_columns = None
        
    def _get_category(self, pattern: str) -> str:
        """Categorize a specific pattern into Creational, Structural, or Behavioral"""
        if pattern in self.CREATIONAL:
            return 'Creational'
        elif pattern in self.STRUCTURAL:
            return 'Structural'
        else:
            return 'Behavioral'
    
    def _download_and_extract_dataset(self) -> str:
        """Download dataset from URL and extract to temp directory"""
        print("Downloading design pattern dataset...")
        
        # Create temp directory
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, "Dp_data.zip")
        
        # Download the file
        response = requests.get(self.DATASET_URL, stream=True)
        if response.status_code == 200:
            with open(zip_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print("Download complete!")
        else:
            raise Exception(f"Failed to download dataset: {response.status_code}")
        
        # Extract the ZIP file
        extract_dir = os.path.join(temp_dir, "Dp_data")
        if zipfile.is_zipfile(zip_path):
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            print(f"Extracted to {extract_dir}")
        else:
            raise Exception("Downloaded file is not a valid ZIP file")
        
        # Return the path to the data
        return os.path.join(extract_dir, "Dp_data")
    
    def _extract_code_features(self, code_content: str, language: str = 'java') -> Dict[str, float]:
        """
        Extract design pattern relevant features from code
        These features approximate CK metrics for pattern detection
        Supports both Java and Python
        """
        features = {}
        lines = code_content.split('\n')
        language_lower = language.lower()
        
        # Basic metrics
        features['loc'] = len(lines)
        
        # Language-specific method and field detection
        if language_lower == 'python':
            # Python methods (def keyword)
            features['totalMethodsQty'] = len(re.findall(r'^\s*def\s+\w+\s*\(', code_content, re.MULTILINE))
            # Python instance variables (self.xxx = )
            features['totalFieldsQty'] = len(set(re.findall(r'self\.(\w+)\s*=', code_content)))
            
            # Python method visibility (convention-based)
            all_methods = re.findall(r'^\s*def\s+(\w+)\s*\(', code_content, re.MULTILINE)
            features['publicMethodsQty'] = len([m for m in all_methods if not m.startswith('_')])
            features['privateMethodsQty'] = len([m for m in all_methods if m.startswith('__') and not m.endswith('__')])
            features['protectedMethodsQty'] = len([m for m in all_methods if m.startswith('_') and not m.startswith('__')])
            features['staticMethodsQty'] = len(re.findall(r'@staticmethod', code_content))
            features['abstractMethodsQty'] = len(re.findall(r'@abstractmethod', code_content))
            features['finalMethodsQty'] = 0  # Python doesn't have final methods
            
            # Python field visibility (convention-based)
            all_fields = set(re.findall(r'self\.(\w+)\s*=', code_content))
            features['publicFieldsQty'] = len([f for f in all_fields if not f.startswith('_')])
            features['privateFieldsQty'] = len([f for f in all_fields if f.startswith('__')])
            features['staticFieldsQty'] = len(re.findall(r'^\s*\w+\s*=\s*[^=]', code_content, re.MULTILINE)) // 2
            features['finalFieldsQty'] = 0
            
            # Python control flow
            features['loopQty'] = len(re.findall(r'\b(for|while)\s+', code_content))
            features['comparisonsQty'] = len(re.findall(r'\bif\s+', code_content))
            features['tryCatchQty'] = len(re.findall(r'\btry\s*:', code_content))
            
            # Python inheritance
            features['noc'] = len(re.findall(r'class\s+\w+\s*\([^)]+\)', code_content))
            features['dit'] = 1 if features['noc'] > 0 else 0
            
            # Python lambdas
            features['lambdasQty'] = len(re.findall(r'\blambda\s+', code_content))
            
            # Python decorators (can indicate patterns)
            features['decoratorCount'] = len(re.findall(r'^@\w+', code_content, re.MULTILINE))
            
        else:
            # Java/C-style methods
            features['totalMethodsQty'] = len(re.findall(r'\b(public|private|protected)?\s*(static)?\s*\w+\s+\w+\s*\([^)]*\)\s*\{', code_content))
            features['totalFieldsQty'] = len(re.findall(r'\b(public|private|protected)?\s*(static)?\s*(final)?\s*\w+\s+\w+\s*[;=]', code_content))
            
            # Method visibility counts
            features['publicMethodsQty'] = len(re.findall(r'\bpublic\s+\w+\s+\w+\s*\(', code_content))
            features['privateMethodsQty'] = len(re.findall(r'\bprivate\s+\w+\s+\w+\s*\(', code_content))
            features['protectedMethodsQty'] = len(re.findall(r'\bprotected\s+\w+\s+\w+\s*\(', code_content))
            features['staticMethodsQty'] = len(re.findall(r'\bstatic\s+\w+\s+\w+\s*\(', code_content))
            features['abstractMethodsQty'] = len(re.findall(r'\babstract\s+\w+\s+\w+\s*\(', code_content))
            features['finalMethodsQty'] = len(re.findall(r'\bfinal\s+\w+\s+\w+\s*\(', code_content))
            
            # Field visibility counts
            features['publicFieldsQty'] = len(re.findall(r'\bpublic\s+(?!class|interface|enum)\w+\s+\w+\s*[;=]', code_content))
            features['privateFieldsQty'] = len(re.findall(r'\bprivate\s+(?!class|interface|enum)\w+\s+\w+\s*[;=]', code_content))
            features['staticFieldsQty'] = len(re.findall(r'\bstatic\s+(?!class|interface|enum)\w+\s+\w+\s*[;=]', code_content))
            features['finalFieldsQty'] = len(re.findall(r'\bfinal\s+(?!class|interface|enum)\w+\s+\w+\s*[;=]', code_content))
            
            # Java control flow
            features['loopQty'] = len(re.findall(r'\b(for|while|do)\s*\(', code_content))
            features['comparisonsQty'] = len(re.findall(r'\bif\s*\(', code_content))
            features['tryCatchQty'] = len(re.findall(r'\btry\s*\{', code_content))
            
            # Java inheritance
            features['noc'] = len(re.findall(r'\bextends\s+\w+', code_content))
            features['dit'] = self._estimate_dit(code_content)
            
            # Java lambdas
            features['lambdasQty'] = len(re.findall(r'->', code_content))
            
            features['decoratorCount'] = 0
        
        # Common metrics
        features['wmc'] = features['totalMethodsQty']  # Weighted Methods per Class
        features['cbo'] = self._count_coupling(code_content, language_lower)  # Coupling Between Objects
        features['rfc'] = features['totalMethodsQty'] + features['cbo']  # Response for Class
        features['lcom'] = self._calculate_lcom(code_content, language_lower)  # Lack of Cohesion
        features['returnQty'] = len(re.findall(r'\breturn\b', code_content))
        
        # Nesting depth
        features['maxNestedBlocksQty'] = self._calculate_nesting(code_content)
        
        # Class structure
        if language_lower == 'python':
            # Python nested classes
            features['innerClassesQty'] = max(0, len(re.findall(r'^\s*class\s+\w+', code_content, re.MULTILINE)) - 1)
            features['anonymousClassesQty'] = 0
        else:
            features['innerClassesQty'] = len(re.findall(r'\bclass\s+\w+.*\{[^}]*class\s+\w+', code_content, re.DOTALL))
            features['anonymousClassesQty'] = len(re.findall(r'new\s+\w+\s*\([^)]*\)\s*\{', code_content))
        
        # Interface/Abstract patterns
        if language_lower == 'python':
            features['interfaceCount'] = len(re.findall(r'class\s+\w+\s*\(\s*ABC\s*\)', code_content))
            features['abstractClassCount'] = len(re.findall(r'@abstractmethod|class\s+\w+\s*\([^)]*ABC[^)]*\)', code_content))
            features['implementsCount'] = features['noc']  # In Python, inheritance serves both purposes
        else:
            features['interfaceCount'] = len(re.findall(r'\binterface\s+\w+', code_content))
            features['abstractClassCount'] = len(re.findall(r'\babstract\s+class\s+\w+', code_content))
            features['implementsCount'] = len(re.findall(r'\bimplements\s+', code_content))
        
        # Design pattern indicators
        features['singletonIndicator'] = self._detect_singleton_pattern(code_content, language_lower)
        features['factoryIndicator'] = self._detect_factory_pattern(code_content)
        features['builderIndicator'] = self._detect_builder_pattern(code_content, language_lower)
        features['observerIndicator'] = self._detect_observer_pattern(code_content)
        features['strategyIndicator'] = self._detect_strategy_pattern(code_content)
        features['decoratorIndicator'] = self._detect_decorator_pattern(code_content, language_lower)
        
        return features
    
    def _estimate_dit(self, code_content: str) -> int:
        """Estimate Depth of Inheritance Tree"""
        extends_count = len(re.findall(r'\bextends\s+\w+', code_content))
        return min(extends_count + 1, 5)  # Cap at 5
    
    def _count_coupling(self, code_content: str, language: str = 'java') -> int:
        """Count coupling (imports and type references)"""
        if language == 'python':
            # Python imports
            imports = len(re.findall(r'^\s*(import|from)\s+', code_content, re.MULTILINE))
            # Class references
            type_refs = len(set(re.findall(r'\b([A-Z][a-zA-Z0-9]*)\s*\(', code_content)))
        else:
            imports = len(re.findall(r'\bimport\s+', code_content))
            type_refs = len(set(re.findall(r'\b([A-Z][a-zA-Z0-9]*)\b', code_content)))
        return min(imports + type_refs // 5, 50)
    
    def _calculate_lcom(self, code_content: str, language: str = 'java') -> float:
        """Estimate Lack of Cohesion in Methods"""
        if language == 'python':
            methods = re.findall(r'^\s*def\s+(\w+)\s*\(', code_content, re.MULTILINE)
            fields = set(re.findall(r'self\.(\w+)\s*=', code_content))
        else:
            methods = re.findall(r'\b(public|private|protected)?\s*\w+\s+(\w+)\s*\([^)]*\)', code_content)
            fields = re.findall(r'\b(public|private|protected)?\s*\w+\s+(\w+)\s*[;=]', code_content)
        
        if len(methods) <= 1:
            return 0
        
        # Simplified LCOM calculation
        return max(0, len(methods) - len(fields) * 2)
    
    def _calculate_nesting(self, code_content: str) -> int:
        """Calculate maximum nesting depth"""
        max_depth = 0
        current_depth = 0
        for char in code_content:
            if char == '{':
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char == '}':
                current_depth = max(0, current_depth - 1)
        return max_depth
    
    def _detect_singleton_pattern(self, code_content: str, language: str = 'java') -> float:
        """Detect Singleton pattern indicators"""
        score = 0.0
        
        if language == 'python':
            # Python Singleton patterns
            # Using __new__ for singleton
            if re.search(r'def\s+__new__\s*\(', code_content):
                score += 0.3
            
            # Class-level instance variable
            if re.search(r'_instance\s*=\s*None', code_content):
                score += 0.3
            
            # get_instance method
            if re.search(r'def\s+get_instance\s*\(', code_content, re.IGNORECASE):
                score += 0.4
            
            # Metaclass singleton
            if re.search(r'class\s+\w+\s*\(.*metaclass', code_content):
                score += 0.3
        else:
            # Private constructor
            if re.search(r'private\s+\w+\s*\(\s*\)', code_content):
                score += 0.3
            
            # Static instance
            if re.search(r'private\s+static\s+\w+\s+instance', code_content, re.IGNORECASE):
                score += 0.3
            
            # getInstance method
            if re.search(r'(public\s+)?static\s+\w+\s+getInstance', code_content):
                score += 0.4
            
        return min(score, 1.0)
    
    def _detect_factory_pattern(self, code_content: str) -> float:
        """Detect Factory pattern indicators"""
        score = 0.0
        
        # Factory in name
        if re.search(r'\bFactory\b', code_content):
            score += 0.3
        
        # create/make methods
        if re.search(r'\b(create|make|build)\w*\s*\(', code_content):
            score += 0.3
        
        # Returns interface/abstract type
        if re.search(r'return\s+new\s+\w+\s*\(', code_content):
            score += 0.2
            
        # Multiple concrete implementations
        if len(re.findall(r'case\s+["\']?\w+["\']?\s*:', code_content)) > 1:
            score += 0.2
            
        return min(score, 1.0)
    
    def _detect_builder_pattern(self, code_content: str, language: str = 'java') -> float:
        """Detect Builder pattern indicators"""
        score = 0.0
        
        # Builder in name
        if re.search(r'\bBuilder\b', code_content):
            score += 0.3
        
        # build() method
        if re.search(r'\bbuild\s*\(\s*\)', code_content):
            score += 0.3
        
        if language == 'python':
            # Method chaining (return self)
            if re.search(r'return\s+self\b', code_content):
                score += 0.2
            
            # with/set methods returning self
            if len(re.findall(r'def\s+(with_|set_)\w+\s*\([^)]*\).*return\s+self', code_content, re.DOTALL)) > 2:
                score += 0.2
        else:
            # Method chaining (return this)
            if re.search(r'return\s+this\s*;', code_content):
                score += 0.2
            
            # with/set methods returning self
            if len(re.findall(r'\b(with|set)\w+\s*\([^)]*\)\s*\{[^}]*return\s+this', code_content)) > 2:
                score += 0.2
            
        return min(score, 1.0)
    
    def _detect_observer_pattern(self, code_content: str) -> float:
        """Detect Observer pattern indicators"""
        score = 0.0
        
        # Observer/Listener keywords
        if re.search(r'\b(Observer|Listener|Subscriber)\b', code_content):
            score += 0.3
        
        # add/remove observer methods
        if re.search(r'\b(add|remove|register|unregister)(Observer|Listener)\b', code_content):
            score += 0.3
        
        # notify/update methods
        if re.search(r'\b(notify|update|on\w+Changed)\b', code_content):
            score += 0.2
            
        # List of observers
        if re.search(r'List<.*?(Observer|Listener)>', code_content):
            score += 0.2
            
        return min(score, 1.0)
    
    def _detect_strategy_pattern(self, code_content: str) -> float:
        """Detect Strategy pattern indicators"""
        score = 0.0
        
        # Strategy keyword
        if re.search(r'\bStrategy\b', code_content):
            score += 0.4
        
        # Interface with single method
        if re.search(r'interface\s+\w+\s*\{[^}]*\w+\s+\w+\s*\([^)]*\)\s*;[^}]*\}', code_content):
            score += 0.3
        
        # setStrategy method
        if re.search(r'\bset\w*Strategy\b', code_content):
            score += 0.3
            
        return min(score, 1.0)
    
    def _detect_decorator_pattern(self, code_content: str, language: str = 'java') -> float:
        """Detect Decorator pattern indicators"""
        score = 0.0
        
        # Decorator keyword
        if re.search(r'\bDecorator\b', code_content):
            score += 0.4
        
        if language == 'python':
            # Python decorators (@decorator)
            decorator_count = len(re.findall(r'^@\w+', code_content, re.MULTILINE))
            if decorator_count > 0:
                score += min(0.3, decorator_count * 0.1)
            
            # Wrapping in __init__
            if re.search(r'def\s+__init__\s*\(\s*self\s*,\s*\w+\s*\)', code_content):
                score += 0.2
            
            # Delegation pattern
            if re.search(r'self\._\w+\s*=\s*\w+', code_content):
                score += 0.2
        else:
            # Wrapping constructor
            if re.search(r'public\s+\w+\s*\(\s*\w+\s+\w+\s*\)', code_content):
                score += 0.2
            
            # Delegation pattern
            if re.search(r'this\.\w+\s*=\s*\w+\s*;', code_content):
                score += 0.2
            
            # Same interface implementation with wrapped object
            if re.search(r'implements\s+\w+', code_content) and re.search(r'private\s+\w+\s+\w+\s*;', code_content):
                score += 0.2
            
        return min(score, 1.0)
    
    def _prepare_features_for_ml(self, features: Dict) -> np.ndarray:
        """Convert extracted features to array format for ML model"""
        # Use the same feature columns that were used during training
        if self.feature_columns is None:
            # Default feature columns based on method.csv structure
            return None
            
        feature_values = []
        for col in self.feature_columns:
            if col in features:
                feature_values.append(features[col])
            else:
                feature_values.append(0)  # Default value for missing features
        
        return np.array([feature_values])
    
    def predict_pattern(self, code_content: str, language: str = 'java') -> Dict[str, Any]:
        """
        Predict design pattern category from code
        Returns the predicted category with confidence scores
        """
        # Extract features
        features = self._extract_code_features(code_content, language)
        
        # If ML model is loaded, use it for prediction
        if self._model_loaded and self.model is not None:
            return self._predict_with_ml(features, code_content)
        
        # Fall back to heuristic-based prediction
        return self._predict_with_heuristics(features, code_content)
    
    def _predict_with_ml(self, features: Dict, code_content: str) -> Dict[str, Any]:
        """Make prediction using trained ML model"""
        # Prepare features for the model
        X = self._prepare_features_for_ml(features)
        
        if X is None or self.scaler is None:
            return self._predict_with_heuristics(features, code_content)
        
        try:
            # Scale features
            X_scaled = self.scaler.transform(X)
            
            # Make prediction
            if TENSORFLOW_AVAILABLE:
                y_pred = self.model.predict(X_scaled, verbose=0)
                predicted_idx = np.argmax(y_pred, axis=1)[0]
                confidence = float(y_pred[0][predicted_idx])
                category_scores = {
                    cls: float(y_pred[0][i]) 
                    for i, cls in enumerate(self.label_encoder.classes_)
                }
            else:
                y_pred = self.model.predict_proba(X)
                predicted_idx = np.argmax(y_pred, axis=1)[0]
                confidence = float(y_pred[0][predicted_idx])
                category_scores = {
                    cls: float(y_pred[0][i]) 
                    for i, cls in enumerate(self.label_encoder.classes_)
                }
            
            predicted = self.label_encoder.classes_[predicted_idx]
            
            # Detect specific patterns
            specific_patterns = self._detect_specific_patterns(features, code_content)
            
            # Suggest a specific pattern
            suggested_pattern = self._suggest_specific_pattern(predicted, features, code_content, specific_patterns)
            
            return {
                'predicted_category': predicted,
                'confidence': round(confidence, 3),
                'category_scores': {k: round(v, 3) for k, v in category_scores.items()},
                'detected_patterns': specific_patterns,
                'suggested_pattern': suggested_pattern,
                'features': {
                    'loc': features.get('loc', 0),
                    'methods': features.get('totalMethodsQty', 0),
                    'fields': features.get('totalFieldsQty', 0),
                    'complexity': features.get('wmc', 0),
                    'coupling': features.get('cbo', 0),
                    'cohesion': features.get('lcom', 0)
                }
            }
        except Exception as e:
            print(f"ML prediction failed: {e}, falling back to heuristics")
            return self._predict_with_heuristics(features, code_content)
    
    def _predict_with_heuristics(self, features: Dict, code_content: str) -> Dict[str, Any]:
        """Make prediction using heuristic rules"""
        # Calculate pattern scores
        pattern_scores = {
            'Creational': 0.0,
            'Structural': 0.0,
            'Behavioral': 0.0
        }
        
        # Creational patterns
        creational_indicators = [
            features.get('singletonIndicator', 0),
            features.get('factoryIndicator', 0),
            features.get('builderIndicator', 0)
        ]
        pattern_scores['Creational'] = max(creational_indicators) * 0.7 + sum(creational_indicators) / 3 * 0.3
        
        # Structural patterns
        structural_indicators = [
            features.get('decoratorIndicator', 0),
            features.get('implementsCount', 0) / max(features.get('totalMethodsQty', 1), 1) * 0.5,
            min(features.get('cbo', 0) / 20, 1.0) * 0.3
        ]
        pattern_scores['Structural'] = max(structural_indicators) * 0.6 + sum(structural_indicators) / 3 * 0.4
        
        # Behavioral patterns
        behavioral_indicators = [
            features.get('observerIndicator', 0),
            features.get('strategyIndicator', 0),
            features.get('interfaceCount', 0) / max(features.get('totalMethodsQty', 1), 1) * 0.5
        ]
        pattern_scores['Behavioral'] = max(behavioral_indicators) * 0.6 + sum(behavioral_indicators) / 3 * 0.4
        
        # Normalize scores
        total = sum(pattern_scores.values())
        if total > 0:
            pattern_scores = {k: v / total for k, v in pattern_scores.items()}
        else:
            pattern_scores = {'Creational': 0.33, 'Structural': 0.33, 'Behavioral': 0.34}
        
        # Get the predicted category
        predicted = max(pattern_scores, key=pattern_scores.get)
        confidence = pattern_scores[predicted]
        
        # Detect specific patterns
        specific_patterns = self._detect_specific_patterns(features, code_content)
        
        # Suggest a specific pattern based on category and code characteristics
        suggested_pattern = self._suggest_specific_pattern(predicted, features, code_content, specific_patterns)
        
        return {
            'predicted_category': predicted,
            'confidence': round(confidence, 3),
            'category_scores': {k: round(v, 3) for k, v in pattern_scores.items()},
            'detected_patterns': specific_patterns,
            'suggested_pattern': suggested_pattern,
            'features': {
                'loc': features.get('loc', 0),
                'methods': features.get('totalMethodsQty', 0),
                'fields': features.get('totalFieldsQty', 0),
                'complexity': features.get('wmc', 0),
                'coupling': features.get('cbo', 0),
                'cohesion': features.get('lcom', 0)
            }
        }
    
    def _suggest_specific_pattern(self, category: str, features: Dict, code_content: str, detected_patterns: List) -> Dict[str, Any]:
        """Suggest the most likely specific pattern based on category and code analysis"""
        
        # If we already detected specific patterns, use the top one
        if detected_patterns:
            top_pattern = detected_patterns[0]
            return {
                'name': top_pattern['name'],
                'category': top_pattern['category'],
                'confidence': top_pattern['confidence'],
                'description': top_pattern['description'],
                'reason': 'Detected through code analysis'
            }
        
        # Pattern suggestions based on category and code characteristics
        code_lower = code_content.lower()
        
        if category == 'Creational':
            # Check for Singleton indicators
            if 'instance' in code_lower and ('private' in code_lower and 'static' in code_lower):
                return {
                    'name': 'Singleton',
                    'category': 'Creational',
                    'confidence': 0.6,
                    'description': 'Ensures a class has only one instance',
                    'reason': 'Static instance field pattern detected'
                }
            # Check for Factory indicators
            elif 'create' in code_lower or 'factory' in code_lower or 'build' in code_lower:
                return {
                    'name': 'Factory Method',
                    'category': 'Creational',
                    'confidence': 0.5,
                    'description': 'Creates objects without specifying exact class',
                    'reason': 'Object creation methods detected'
                }
            # Check for Builder indicators
            elif 'builder' in code_lower or ('set' in code_lower and 'return this' in code_lower):
                return {
                    'name': 'Builder',
                    'category': 'Creational',
                    'confidence': 0.5,
                    'description': 'Separates object construction from representation',
                    'reason': 'Fluent builder pattern detected'
                }
            else:
                return {
                    'name': 'Factory Method',
                    'category': 'Creational',
                    'confidence': 0.4,
                    'description': 'Creates objects without specifying exact class',
                    'reason': 'Default suggestion for Creational category'
                }
        
        elif category == 'Structural':
            # Check for Adapter indicators
            if 'adapter' in code_lower or 'wrapper' in code_lower:
                return {
                    'name': 'Adapter',
                    'category': 'Structural',
                    'confidence': 0.6,
                    'description': 'Converts interface of a class into another interface',
                    'reason': 'Adapter/wrapper pattern detected'
                }
            # Check for Decorator indicators
            elif 'decorator' in code_lower or ('component' in code_lower and 'wrapped' in code_lower):
                return {
                    'name': 'Decorator',
                    'category': 'Structural',
                    'confidence': 0.5,
                    'description': 'Attaches additional responsibilities dynamically',
                    'reason': 'Decorator pattern indicators detected'
                }
            # Check for Facade indicators
            elif features.get('totalMethodsQty', 0) > 5 and features.get('cbo', 0) > 3:
                return {
                    'name': 'Facade',
                    'category': 'Structural',
                    'confidence': 0.5,
                    'description': 'Provides simplified interface to complex subsystem',
                    'reason': 'High coupling suggests facade pattern'
                }
            else:
                return {
                    'name': 'Facade',
                    'category': 'Structural',
                    'confidence': 0.4,
                    'description': 'Provides simplified interface to complex subsystem',
                    'reason': 'Default suggestion for Structural category'
                }
        
        elif category == 'Behavioral':
            # Check for Observer indicators
            if 'observer' in code_lower or 'listener' in code_lower or 'subscribe' in code_lower:
                return {
                    'name': 'Observer',
                    'category': 'Behavioral',
                    'confidence': 0.6,
                    'description': 'Defines subscription mechanism for event notification',
                    'reason': 'Observer/listener pattern detected'
                }
            # Check for Strategy indicators
            elif 'strategy' in code_lower or 'algorithm' in code_lower:
                return {
                    'name': 'Strategy',
                    'category': 'Behavioral',
                    'confidence': 0.5,
                    'description': 'Defines family of interchangeable algorithms',
                    'reason': 'Strategy pattern indicators detected'
                }
            # Check for Command indicators
            elif 'command' in code_lower or 'execute' in code_lower:
                return {
                    'name': 'Command',
                    'category': 'Behavioral',
                    'confidence': 0.5,
                    'description': 'Encapsulates request as an object',
                    'reason': 'Command/execute pattern detected'
                }
            # Check for State indicators
            elif 'state' in code_lower and features.get('totalMethodsQty', 0) > 3:
                return {
                    'name': 'State',
                    'category': 'Behavioral',
                    'confidence': 0.5,
                    'description': 'Allows object to alter behavior when state changes',
                    'reason': 'State management pattern detected'
                }
            else:
                return {
                    'name': 'Strategy',
                    'category': 'Behavioral',
                    'confidence': 0.4,
                    'description': 'Defines family of interchangeable algorithms',
                    'reason': 'Default suggestion for Behavioral category'
                }
        
        # Fallback
        return {
            'name': 'Unknown',
            'category': category,
            'confidence': 0.3,
            'description': 'Could not determine specific pattern',
            'reason': 'Insufficient pattern indicators'
        }
    
    def _detect_specific_patterns(self, features: Dict, code_content: str) -> List[Dict[str, Any]]:
        """Detect specific design patterns present in the code"""
        patterns = []
        
        # Check each pattern indicator
        pattern_checks = [
            ('Singleton', features.get('singletonIndicator', 0), 'Creational',
             'Ensures a class has only one instance and provides global access to it'),
            ('Factory', features.get('factoryIndicator', 0), 'Creational',
             'Creates objects without specifying the exact class to create'),
            ('Builder', features.get('builderIndicator', 0), 'Creational',
             'Separates object construction from its representation'),
            ('Observer', features.get('observerIndicator', 0), 'Behavioral',
             'Defines a subscription mechanism to notify multiple objects about events'),
            ('Strategy', features.get('strategyIndicator', 0), 'Behavioral',
             'Defines a family of algorithms and makes them interchangeable'),
            ('Decorator', features.get('decoratorIndicator', 0), 'Structural',
             'Attaches additional responsibilities to objects dynamically'),
        ]
        
        for name, score, category, description in pattern_checks:
            if score > 0.3:  # Threshold for detection
                patterns.append({
                    'name': name,
                    'category': category,
                    'confidence': round(score, 2),
                    'description': description
                })
        
        # Sort by confidence
        patterns.sort(key=lambda x: x['confidence'], reverse=True)
        
        return patterns
    
    def train_model(self, data_path: str = None):
        """
        Train the design pattern detection model using CK metrics
        Downloads dataset from URL if not provided
        """
        # Download dataset if path not provided
        if data_path is None:
            data_path = self._download_and_extract_dataset()
        
        tr_path = os.path.join(data_path, 'Dp_trainset')
        te_path = os.path.join(data_path, 'Dp_testset')
        
        if not os.path.exists(tr_path):
            print(f"Training data not found at {tr_path}")
            return False
        
        print("Loading training data...")
        
        # Get method.csv files
        # Path structure: Dp_trainset/Pattern_name/project_name/ckmetrics/method.csv
        # Need to go up 3 levels to get Pattern_name (not project_name)
        tr_files = [(f, os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(f))))) 
                    for f in glob.glob(os.path.join(tr_path, "**", "*method.csv"), recursive=True)]
        te_files = [(f, os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(f))))) 
                    for f in glob.glob(os.path.join(te_path, "**", "*method.csv"), recursive=True)]
        
        print(f"Found {len(tr_files)} training files, {len(te_files)} test files")
        
        # Process files
        trainset = self._process_metric_files(tr_files)
        testset = self._process_metric_files(te_files)
        
        if trainset is None or len(trainset) == 0:
            print("No valid training data")
            return False
        
        print(f"Trainset shape: {trainset.shape}")
        print(f"Testset shape: {testset.shape if testset is not None else 'None'}")
        
        # Prepare features
        self.feature_columns = [c for c in trainset.columns if c != 'Design Pattern']
        
        X_train = trainset.drop(['Design Pattern'], axis=1)
        y_train = trainset['Design Pattern']
        
        if testset is not None and len(testset) > 0:
            X_test = testset.drop(['Design Pattern'], axis=1)
            y_test = testset['Design Pattern']
        else:
            from sklearn.model_selection import train_test_split
            X_train, X_test, y_train, y_test = train_test_split(X_train, y_train, test_size=0.2, random_state=42)
        
        # Encode labels
        y_train_encoded = self.label_encoder.fit_transform(y_train)
        y_test_encoded = self.label_encoder.transform(y_test)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        if TENSORFLOW_AVAILABLE:
            # Use TensorFlow/Keras
            y_train_cat = to_categorical(y_train_encoded)
            y_test_cat = to_categorical(y_test_encoded)
            
            self.model = Sequential([
                Dense(64, input_dim=X_train_scaled.shape[1], activation='relu'),
                Dropout(0.3),
                Dense(32, activation='relu'),
                Dropout(0.2),
                Dense(len(self.label_encoder.classes_), activation='softmax')
            ])
            
            self.model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
            self.model.fit(X_train_scaled, y_train_cat, validation_split=0.2, epochs=50, batch_size=32, verbose=1)
            
            # Evaluate
            loss, accuracy = self.model.evaluate(X_test_scaled, y_test_cat, verbose=0)
            print(f"\nTest Accuracy: {accuracy * 100:.2f}%")
        else:
            # Use sklearn
            self.model = MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=500, random_state=42)
            self.model.fit(X_train_scaled, y_train_encoded)
            
            # Evaluate
            accuracy = self.model.score(X_test_scaled, y_test_encoded)
            print(f"\nTest Accuracy: {accuracy * 100:.2f}%")
        
        # Save model
        self.save_model()
        self._model_loaded = True
        
        return True
    
    def _process_metric_files(self, files: List[Tuple[str, str]]) -> pd.DataFrame:
        """Process CK metric files into a dataset"""
        data_frames = []
        
        for file_path, pattern_name in files:
            try:
                df = pd.read_csv(file_path)
                
                # Drop identifier columns if they exist
                cols_to_drop = [c for c in ['file', 'class', 'method'] if c in df.columns]
                if cols_to_drop:
                    df = df.drop(cols_to_drop, axis=1)
                
                if df.empty:
                    continue
                
                # Fill missing values with mode or 0
                for col in df.columns:
                    if df[col].isna().any():
                        mode_val = df[col].mode()
                        df[col].fillna(mode_val.iloc[0] if len(mode_val) > 0 else 0, inplace=True)
                
                # Sum numeric columns to get aggregate metrics
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                agg_row = df[numeric_cols].sum()
                
                # Get pattern category
                category = self._get_category(pattern_name)
                
                # Create single row DataFrame
                row_df = pd.DataFrame([agg_row])
                row_df['Design Pattern'] = category
                
                data_frames.append(row_df)
                
            except Exception as e:
                continue
        
        if not data_frames:
            return None
        
        result = pd.concat(data_frames, ignore_index=True)
        return result
    
    def save_model(self):
        """Save the trained model"""
        model_data = {
            'scaler': self.scaler,
            'label_encoder': self.label_encoder,
            'feature_columns': self.feature_columns
        }
        
        # Save preprocessing data
        joblib.dump(model_data, f"{self.model_path}_preprocessing.pkl")
        
        # Save the model
        if TENSORFLOW_AVAILABLE and self.model is not None:
            self.model.save(f"{self.model_path}.keras")
        elif self.model is not None:
            joblib.dump(self.model, f"{self.model_path}_sklearn.pkl")
        
        print(f"Model saved to {self.model_path}")
    
    def load_model(self) -> bool:
        """Load a trained model"""
        try:
            preprocessing_path = f"{self.model_path}_preprocessing.pkl"
            
            if os.path.exists(preprocessing_path):
                model_data = joblib.load(preprocessing_path)
                self.scaler = model_data['scaler']
                self.label_encoder = model_data['label_encoder']
                self.feature_columns = model_data.get('feature_columns')
            else:
                return False
            
            # Try loading TensorFlow model
            keras_path = f"{self.model_path}.keras"
            if TENSORFLOW_AVAILABLE and os.path.exists(keras_path):
                self.model = load_model(keras_path)
                self._model_loaded = True
                print(f"Loaded TensorFlow model from {keras_path}")
                return True
            
            # Try loading sklearn model
            sklearn_path = f"{self.model_path}_sklearn.pkl"
            if os.path.exists(sklearn_path):
                self.model = joblib.load(sklearn_path)
                self._model_loaded = True
                print(f"Loaded sklearn model from {sklearn_path}")
                return True
            
            return False
            
        except Exception as e:
            print(f"Failed to load model: {e}")
            return False
    
    def get_pattern_summary(self, code_content: str, language: str = 'java') -> Dict[str, Any]:
        """Get a comprehensive design pattern analysis summary"""
        prediction = self.predict_pattern(code_content, language)
        
        return {
            'design_patterns': {
                'predicted_category': prediction['predicted_category'],
                'confidence': prediction['confidence'],
                'category_probabilities': prediction['category_scores'],
                'detected_patterns': prediction['detected_patterns'],
                'suggested_pattern': prediction.get('suggested_pattern', {}),
                'code_metrics': prediction['features'],
                'analysis_method': 'deep_learning' if self._model_loaded else 'heuristic'
            }
        }


def main():
    """Test the design pattern detector"""
    detector = DesignPatternDetector()
    
    # Try to load existing model
    if not detector.load_model():
        print("No trained model found. Training new model...")
        detector.train_model()
    
    # Test with sample Singleton code
    singleton_code = '''
    public class Singleton {
        private static Singleton instance;
        
        private Singleton() {}
        
        public static Singleton getInstance() {
            if (instance == null) {
                instance = new Singleton();
            }
            return instance;
        }
    }
    '''
    
    print("\nTesting Singleton pattern detection:")
    result = detector.predict_pattern(singleton_code)
    print(f"Predicted: {result['predicted_category']} (confidence: {result['confidence']:.2f})")
    print(f"Detected patterns: {result['detected_patterns']}")
    
    # Test with sample Factory code
    factory_code = '''
    public interface Shape {
        void draw();
    }
    
    public class Circle implements Shape {
        public void draw() {
            System.out.println("Drawing Circle");
        }
    }
    
    public class ShapeFactory {
        public Shape createShape(String type) {
            switch(type) {
                case "CIRCLE": return new Circle();
                case "SQUARE": return new Square();
                default: return null;
            }
        }
    }
    '''
    
    print("\nTesting Factory pattern detection:")
    result = detector.predict_pattern(factory_code)
    print(f"Predicted: {result['predicted_category']} (confidence: {result['confidence']:.2f})")
    print(f"Detected patterns: {result['detected_patterns']}")
    
    # Test with Observer code
    observer_code = '''
    public interface Observer {
        void update(String message);
    }
    
    public class Subject {
        private List<Observer> observers = new ArrayList<>();
        
        public void addObserver(Observer o) {
            observers.add(o);
        }
        
        public void removeObserver(Observer o) {
            observers.remove(o);
        }
        
        public void notifyObservers(String message) {
            for (Observer o : observers) {
                o.update(message);
            }
        }
    }
    '''
    
    print("\nTesting Observer pattern detection:")
    result = detector.predict_pattern(observer_code)
    print(f"Predicted: {result['predicted_category']} (confidence: {result['confidence']:.2f})")
    print(f"Detected patterns: {result['detected_patterns']}")


if __name__ == "__main__":
    main()
