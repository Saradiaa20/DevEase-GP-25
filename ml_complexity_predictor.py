import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import GradientBoostingClassifier, VotingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
import joblib
import os
from typing import Dict, List, Tuple, Any

class ComplexityPredictor:
    """
    Machine Learning model for predicting code complexity based on code features
    """
    
    def __init__(self, model_path="complexity_model.pkl"):
        self.model_path = model_path
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.imputer = SimpleImputer(strategy='median')
        self.feature_columns = [
            'no_of_ifs', 'no_of_loop', 'no_of_break', 'priority_queue_present',
            'no_of_sort', 'hash_set_present', 'hash_map_present', 'recursion_present',
            'nested_loop_depth'
        ]
        self.complexity_mapping = {
            '1': 'O(1)',
            'logn': 'O(log n)',
            'n': 'O(n)',
            'n_square': 'O(n²)',
            'nlogn': 'O(n log n)'
        }

    def verify_preprocessing(self, csv_path: str) -> bool:
        """
        Run preprocessing silently and only return a success/failure message.
        This does NOT print any detailed preprocessing logs.
        """
        try:
            # 1. Load CSV
            df = pd.read_csv(csv_path)

            # 2. Check required columns exist
            for col in self.feature_columns + ['complexity']:
                if col not in df.columns:
                    print(f"❌ ERROR: Missing required column: {col}")
                    return False

            # 3. Handle missing values quietly
            df = df.dropna()

            # 4. Remove duplicates quietly
            df = df.drop_duplicates()

            # 5. Extract feature matrix
            X = df[self.feature_columns]

            # 6. Impute quietly
            self.imputer.fit_transform(X)

            # 7. Scale quietly
            self.scaler.fit_transform(X)

            # 8. Encode labels quietly
            y = df['complexity'].values
            self.label_encoder.fit_transform(y)

            print("Preprocessing completed successfully.")
            return True

        except Exception as e:
            print(f"Preprocessing failed: {e}")
            return False

    
    def load_dataset(self, csv_path: str) -> pd.DataFrame:
        """Load and preprocess the dataset with advanced preprocessing"""
        try:
            df = pd.read_csv(csv_path)
            # print(f"Dataset loaded: {len(df)} samples")
            # print(f"Features: {list(df.columns)}")
            
            # Advanced Data Preprocessing
            # print("\nAdvanced Data Preprocessing:")
            # print("-" * 50)
            
            # Check for missing values
            missing_values = df.isnull().sum()
            if missing_values.any():
                print(f"WARNING: Missing values found: {missing_values[missing_values > 0]}")
                df = df.dropna()  # Remove rows with missing values
                print(f"SUCCESS: After removing missing values: {len(df)} samples")
            # else:
            #     print("SUCCESS: No missing values found")
            
            # Check for duplicate rows
            duplicates = df.duplicated().sum()
            if duplicates > 0:
                print(f"WARNING: Found {duplicates} duplicate rows, removing...")
                df = df.drop_duplicates()
                print(f"SUCCESS: After removing duplicates: {len(df)} samples")
            # else:
            #     print("SUCCESS: No duplicate rows found")
            
            # Data type validation
            # print("\nData types validation:")
            # for col in self.feature_columns:
            #     if col in df.columns:
            #         print(f"  {col}: {df[col].dtype}")
            
            # Advanced outlier analysis
            numerical_features = ['no_of_ifs', 'no_of_loop', 'no_of_break', 'no_of_sort', 'nested_loop_depth']
            # print("\nOutlier analysis (IQR method):")
            for feature in numerical_features:
                if feature in df.columns:
                    Q1 = df[feature].quantile(0.25)
                    Q3 = df[feature].quantile(0.75)
                    IQR = Q3 - Q1
                    outliers = df[(df[feature] < Q1 - 1.5 * IQR) | (df[feature] > Q3 + 1.5 * IQR)]
                    outlier_percentage = len(outliers)/len(df)*100
                    # print(f"  {feature}: {len(outliers)} outliers ({outlier_percentage:.1f}%)")
            
            # print("\nComplexity distribution:")
            # print(df['complexity'].value_counts())
            
            return df
        except Exception as e:
            print(f"ERROR: Error loading dataset: {e}")
            return None
    
    def prepare_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features and target for training with advanced preprocessing"""
        # print("\nAdvanced Feature Engineering:")
        # print("-" * 50)
        
        # Select feature columns
        X = df[self.feature_columns].copy()
        
        # Handle missing values with imputation
        # print("Applying missing value imputation...")
        X_imputed = self.imputer.fit_transform(X)
        
        # Feature scaling (StandardScaler) for better model performance
        # print("Applying feature scaling (StandardScaler)...")
        X_scaled = self.scaler.fit_transform(X_imputed)
        
        # Encode complexity labels properly
        # print("Encoding complexity labels...")
        y = df['complexity'].values
        y_encoded = self.label_encoder.fit_transform(y)
        
        # print(f"Original features shape: {X.shape}")
        # print(f"After imputation: {X_imputed.shape}")
        # print(f"After scaling: {X_scaled.shape}")
        # print(f"Target shape: {y_encoded.shape}")
        
        # Feature statistics after scaling
        # print("\nFeature statistics (after scaling):")
        # for i, feature in enumerate(self.feature_columns):
        #     print(f"  {feature}: mean={X_scaled[:, i].mean():.3f}, std={X_scaled[:, i].std():.3f}")
        
        # # Label encoding mapping
        # # print("\nLabel encoding mapping:")
        # for i, label in enumerate(self.label_encoder.classes_):
        #     print(f"  {label} -> {i}")
        
        return X_scaled, y_encoded
    
    def train_model(self, csv_path: str, test_size: float = 0.2, random_state: int = 42, force_retrain: bool = False):
        """Train multiple models (RF, SVM, NN, GB, KNN) and compare their performance"""
        # Check if model already exists and is recent
        if not force_retrain and os.path.exists(self.model_path):
            try:
                # Try to load existing model
                self.model = joblib.load(self.model_path)
                print("Existing ML model found and loaded successfully!")
                return True
            except:
                print("Existing model corrupted, retraining...")
        
        # print("=" * 60)
        # print("Training Complexity Prediction Model")
        # print("=" * 60)
        
        # Load dataset
        df = self.load_dataset(csv_path)
        if df is None:
            return False
        
        # Prepare features
        X, y = self.prepare_features(df)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        # print(f"Training set: {X_train.shape[0]} samples")
        # print(f"Test set: {X_test.shape[0]} samples")
        
        # Train Random Forest model
        # print("\nTraining Random Forest model...")
        # self.model = RandomForestClassifier(
        #     n_estimators=100,
        #     random_state=random_state,
        #     max_depth=10,
        #     min_samples_split=5,
        #     min_samples_leaf=2
        # )

        # Train (RF, SVM, NN, GB, KNN) models
        models = {
            "RandomForest": RandomForestClassifier(
                n_estimators=100, random_state=random_state,
                max_depth=10, min_samples_split=5, min_samples_leaf=2, class_weight='balanced', max_features='sqrt'
            ),
            "LinearSVM": SVC(kernel='rbf', probability=True, random_state=random_state, class_weight='balanced', C=1.0, gamma='scale'),
            "NeuralNetwork": MLPClassifier(hidden_layer_sizes=(128, 64, 32), max_iter=2000, random_state=random_state),
            "KNN": KNeighborsClassifier(n_neighbors=20)
        }

        results = {}
        best_accuracy = 0
        best_model_name = None
        
        # Train and evaluate all models
        for name, model in models.items():
            # print(f"\n{'-' * 50}\nTraining model: {name}")
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            # print(f"✅ {name} Accuracy: {accuracy:.4f}")
            results[name] = accuracy

            # Keep track of best model
            if accuracy > best_accuracy:
                best_accuracy = accuracy
                best_model_name = name
                self.model = model
        print("-"*50)
        print("\nML tranined models")
        print("\nModel Comparison Results:")
        for name, accuracy in results.items():
            print(f"  {name}: {accuracy:.4f}")

        print(f"\nBest model selected: {best_model_name} with accuracy {best_accuracy:.4f}")

        # # Hybrid ensemble model (mix Random Forest + Neural Network + SVM)
        # print(f"\n{'=' * 70}")
        # print("🔸 Creating Hybrid Ensemble Model (RF + KNN + NN)")
        # ensemble = VotingClassifier(
        #     estimators=[
        #         ('rf', models["RandomForest"]),
        #         ('knn', models["KNN"]),
        #         ('nn', models["NeuralNetwork"])
        #     ],
        #     voting='soft'
        # )

        # ensemble.fit(X_train, y_train)
        # y_pred_ensemble = ensemble.predict(X_test)
        # ensemble_accuracy = accuracy_score(y_test, y_pred_ensemble)
        # print(f"✨ Hybrid Ensemble Accuracy: {ensemble_accuracy:.4f}")

        # results["HybridEnsemble"] = ensemble_accuracy

        # # Choose the final best model
        # if ensemble_accuracy > best_accuracy:
        #     print("🔹 Hybrid Ensemble selected as the final model.")
        #     self.model = ensemble
        #     best_model_name = "HybridEnsemble"
        #     best_accuracy = ensemble_accuracy
        # else:
        #     print(f"🔹 {best_model_name} selected as the final model.")

        # # Print comparison summary
        # print(f"\n{'=' * 70}")
        # print("📊 Model Comparison Summary")
        # print("=" * 70)
        # for model_name, acc in results.items():
        #     print(f"{model_name:<20} : {acc:.4f}")
        # print(f"\n🏆 Best Model: {best_model_name} with Accuracy = {best_accuracy:.4f}")

        # Evaluate final model
        y_pred_final = self.model.predict(X_test)
        print("\nFinal Model Classification Report:")
        print(classification_report(y_test, y_pred_final))

        # Save model
        self.save_model()
        print("Final model saved Successfully.")
        return True

        # self.model.fit(X_train, y_train)
        
        # # Evaluate model
        # y_pred = self.model.predict(X_test)
        # accuracy = accuracy_score(y_test, y_pred)
        
        # print("\nModel Performance:")
        # print(f"Accuracy: {accuracy:.4f}")
        # print("\nClassification Report:")
        # print(classification_report(y_test, y_pred))
        
        # # Save model
        # self.save_model()
        
        # print(f"\nModel saved to: {self.model_path}")
        # return True
    
    def save_model(self):
        """Save the trained model and preprocessing objects"""
        if self.model is not None:
            # Save model and all preprocessing objects
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'label_encoder': self.label_encoder,
                'imputer': self.imputer
            }
            joblib.dump(model_data, self.model_path)
            # print("SUCCESS: Model and preprocessing objects saved successfully!")
        else:
            print("ERROR: No model to save!")
    
    def load_model(self):
        """Load a pre-trained model and preprocessing objects"""
        try:
            if os.path.exists(self.model_path):
                model_data = joblib.load(self.model_path)
                
                # Handle both old format (just model) and new format (with preprocessing)
                if isinstance(model_data, dict):
                    self.model = model_data['model']
                    self.scaler = model_data['scaler']
                    self.label_encoder = model_data['label_encoder']
                    self.imputer = model_data['imputer']
                    print(f"SUCCESS: Model and preprocessing objects loaded from: {self.model_path}")
                else:
                    # Old format - just the model
                    self.model = model_data
                    print(f"WARNING: Model loaded from: {self.model_path} (legacy format - no preprocessing)")
                
                return True
            else:
                print(f"ERROR: Model file not found: {self.model_path}")
                return False
        except Exception as e:
            print(f"ERROR: Error loading model: {e}")
            return False
    
    def predict_complexity(self, features: Dict[str, int]) -> Dict[str, Any]:
        """Predict complexity for given features with advanced preprocessing"""
        if self.model is None:
            if not self.load_model():
                return {"error": "No trained model available"}
        
        try:
            # # Prepare feature vector in the same order as training
            feature_vector = np.array([[
                features.get('no_of_ifs', 0),
                features.get('no_of_loop', 0),
                features.get('no_of_break', 0),
                features.get('priority_queue_present', 0),
                features.get('no_of_sort', 0),
                features.get('hash_set_present', 0),
                features.get('hash_map_present', 0),
                features.get('recursion_present', 0),
                features.get('nested_loop_depth', 0)
            ]])

            # Build a DataFrame with EXACT SAME columns as training
            X = pd.DataFrame([{
                'no_of_ifs': features.get('no_of_ifs', 0),
                'no_of_loop': features.get('no_of_loop', 0),
                'no_of_break': features.get('no_of_break', 0),
                'priority_queue_present': features.get('priority_queue_present', 0),
                'no_of_sort': features.get('no_of_sort', 0),
                'hash_set_present': features.get('hash_set_present', 0),
                'hash_map_present': features.get('hash_map_present', 0),
                'recursion_present': features.get('recursion_present', 0),
                'nested_loop_depth': features.get('nested_loop_depth', 0)
            }], columns=self.feature_columns)
            
            # Apply same preprocessing as training
            feature_vector_imputed = self.imputer.transform(feature_vector)
            feature_vector_scaled = self.scaler.transform(feature_vector_imputed)
            
            # Apply imputer and scaler (no warnings now)
            X_imputed = self.imputer.transform(X)
            X_scaled = self.scaler.transform(X_imputed)

            # Make prediction
            prediction_encoded = self.model.predict(X_scaled)[0]
            probabilities = self.model.predict_proba(X_scaled)[0]

            # Decode prediction back to original label
            # prediction = self.label_encoder.inverse_transform([prediction_encoded])[0]
            prediction = self.label_encoder.inverse_transform([prediction_encoded])[0]


            # Get class names and probabilities
            class_names = self.label_encoder.classes_
            prob_dict = {class_names[i]: probabilities[i] for i in range(len(class_names))}
            
            return {
                "predicted_complexity": prediction,
                "complexity_description": self.complexity_mapping.get(prediction, prediction),
                "confidence": max(probabilities),
                "all_probabilities": prob_dict
            }
            
        except Exception as e:
            return {"error": f"Prediction failed: {e}"}
    
    def extract_features_from_code(self, code_content: str) -> Dict[str, int]:
        """Extract complexity features from code content"""
        features = {
            'no_of_ifs': 0,
            'no_of_loop': 0,
            'no_of_break': 0,
            'priority_queue_present': 0,
            'no_of_sort': 0,
            'hash_set_present': 0,
            'hash_map_present': 0,
            'recursion_present': 0,
            'nested_loop_depth': 0
        }
        
        lines = code_content.split('\n')
        
        # Count basic features
        for line in lines:
            line_lower = line.lower().strip()
            
            # Count if statements
            if 'if ' in line_lower or 'if(' in line_lower:
                features['no_of_ifs'] += 1
            
            # Count loops
            if any(loop in line_lower for loop in ['for ', 'while ', 'do ']):
                features['no_of_loop'] += 1
            
            # Count break statements
            if 'break' in line_lower:
                features['no_of_break'] += 1
            
            # Check for data structures
            if 'priorityqueue' in line_lower or 'priority_queue' in line_lower:
                features['priority_queue_present'] = 1
            
            if 'sort' in line_lower or 'sorted' in line_lower:
                features['no_of_sort'] += 1
            
            if 'hashset' in line_lower or 'set' in line_lower:
                features['hash_set_present'] = 1
            
            if 'hashmap' in line_lower or 'map' in line_lower:
                features['hash_map_present'] = 1
            
            # Check for recursion (simplified)
            if 'return' in line_lower and any(func in line_lower for func in ['self.', 'this.']):
                features['recursion_present'] = 1
        
        # Calculate nested loop depth (simplified)
        max_depth = 0
        current_depth = 0
        
        for line in lines:
            line_lower = line.strip()
            if any(loop in line_lower for loop in ['for ', 'while ', 'do ']):
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif line_lower.startswith('}') or line_lower.startswith('end'):
                current_depth = max(0, current_depth - 1)
        
        features['nested_loop_depth'] = max_depth
        
        return features
    
    def print_prediction_report(self, prediction_result: Dict[str, Any]):
        """Print a formatted prediction report"""
        if "error" in prediction_result:
            print(f"ERROR: {prediction_result['error']}")
            return
        
        print("\nML Complexity Prediction Report")
        print("=" * 50)
        print(f"Predicted Complexity: {prediction_result['predicted_complexity']}")
        print(f"Description: {prediction_result['complexity_description']}")
        print(f"Confidence: {prediction_result['confidence']:.2%}")
        
        # print("\nAll Complexity Probabilities:")
        # for complexity, prob in prediction_result['all_probabilities'].items():
        #     desc = self.complexity_mapping.get(complexity, complexity)
        #     print(f"  {desc}: {prob:.2%}")

def main():
    """Main function to train the model"""
    predictor = ComplexityPredictor()
    
    # Train the model with force retrain to see advanced preprocessing
    dataset_path = os.path.join(os.path.dirname(__file__), "dataset1.csv")
    success = predictor.train_model(dataset_path, force_retrain=True)
    
    if success:
        print("\n" + "=" * 60)
        print("Training completed successfully!")
        print("Model is ready for predictions.")
        print("=" * 60)
    else:
        print("Training failed!")

if __name__ == "__main__":
    main()
