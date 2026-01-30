#!/usr/bin/env python3
"""
Verification Script: Ensures ML and Backend Analysis is Working Correctly
Run this script to verify that your analysis pipeline is using ML models correctly.
"""

import os
import sys
import json
import tempfile
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def print_header(text):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def print_success(text):
    print(f"✓ {text}")

def print_error(text):
    print(f"✗ {text}")

def print_warning(text):
    print(f"⚠ {text}")

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        print_success(f"{description}: {filepath} ({size:,} bytes)")
        return True
    else:
        print_error(f"{description}: {filepath} NOT FOUND")
        return False

def verify_ml_model():
    """Verify ML model and dataset"""
    print_header("1. ML Model & Dataset Verification")
    
    model_path = project_root / "complexity_model.pkl"
    dataset_path = project_root / "dataset1.csv"
    
    model_exists = check_file_exists(model_path, "ML Model")
    dataset_exists = check_file_exists(dataset_path, "Dataset")
    
    if not dataset_exists:
        print_warning("Dataset not found. ML model cannot be trained without dataset1.csv")
        return False
    
    if not model_exists:
        print_warning("ML model not found. Will attempt to train...")
        try:
            from ml_complexity_predictor import ComplexityPredictor
            predictor = ComplexityPredictor()
            print("Training ML model...")
            success = predictor.train_model(str(dataset_path), force_retrain=True)
            if success:
                print_success("ML model trained successfully!")
                return True
            else:
                print_error("ML model training failed")
                return False
        except Exception as e:
            print_error(f"Error training model: {e}")
            return False
    
    return True

def verify_ml_prediction():
    """Verify ML model can make predictions"""
    print_header("2. ML Prediction Verification")
    
    try:
        from ml_complexity_predictor import ComplexityPredictor
        
        predictor = ComplexityPredictor()
        
        # Test with simple code
        test_code = """
def example_function(n):
    for i in range(n):
        print(i)
"""
        
        print("Extracting features from test code...")
        features = predictor.extract_features_from_code(test_code)
        print(f"Extracted features: {features}")
        
        print("Making ML prediction...")
        prediction = predictor.predict_complexity(features)
        
        if "error" in prediction:
            print_error(f"ML prediction failed: {prediction['error']}")
            return False
        
        print_success(f"ML Prediction: {prediction.get('predicted_complexity', 'N/A')}")
        print_success(f"Description: {prediction.get('complexity_description', 'N/A')}")
        print_success(f"Confidence: {prediction.get('confidence', 0):.2%}")
        
        if prediction.get('confidence', 0) < 0.3:
            print_warning("Low confidence prediction - model may need retraining")
        
        return True
        
    except Exception as e:
        print_error(f"Error testing ML prediction: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_backend_modules():
    """Verify all backend modules are importable"""
    print_header("3. Backend Modules Verification")
    
    modules = [
        ("parsing", "ASTParser"),
        ("code_smell_detector", "CodeSmellDetector"),
        ("code_quality_metrics", "CodeQualityAnalyzer"),
        ("ml_complexity_predictor", "ComplexityPredictor"),
        ("technical_debt_calculator", "TechnicalDebtCalculator"),
        ("feature_router", "FeatureRouter"),
    ]
    
    all_ok = True
    for module_name, class_name in modules:
        try:
            module = __import__(module_name)
            cls = getattr(module, class_name)
            print_success(f"{module_name}.{class_name} imported successfully")
        except Exception as e:
            print_error(f"{module_name}.{class_name} import failed: {e}")
            all_ok = False
    
    return all_ok

def verify_analysis_pipeline():
    """Verify complete analysis pipeline"""
    print_header("4. Complete Analysis Pipeline Verification")
    
    try:
        from feature_router import FeatureRouter
        
        router = FeatureRouter()
        
        # Create test file
        test_code = """
def calculate_sum(numbers):
    total = 0
    for num in numbers:
        total += num
    return total

class Calculator:
    def add(self, a, b):
        return a + b
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            tmp_path = f.name
        
        try:
            print("Running complete analysis pipeline...")
            result = router.analyze_code(file_path=tmp_path)
            
            # Check required fields
            required_fields = [
                'language',
                'code_smells',
                'quality_score',
                'ml_complexity',
                'technical_debt',
                'analysis_metadata'
            ]
            
            missing_fields = []
            for field in required_fields:
                if field not in result:
                    missing_fields.append(field)
                else:
                    print_success(f"Field '{field}' present in results")
            
            if missing_fields:
                print_error(f"Missing fields: {missing_fields}")
                return False
            
            # Verify ML complexity is present and valid
            ml_complexity = result.get('ml_complexity', {})
            if 'error' in ml_complexity.get('prediction', {}):
                print_error(f"ML prediction error: {ml_complexity['prediction']['error']}")
                return False
            
            if 'prediction' not in ml_complexity:
                print_error("ML prediction missing from results")
                return False
            
            prediction = ml_complexity['prediction']
            if 'predicted_complexity' not in prediction:
                print_error("predicted_complexity missing from ML prediction")
                return False
            
            print_success(f"ML Complexity: {prediction.get('predicted_complexity')}")
            print_success(f"ML Confidence: {prediction.get('confidence', 0):.2%}")
            
            # Verify analysis metadata mentions ML
            metadata = result.get('analysis_metadata', {})
            modules_used = metadata.get('modules_used', [])
            if 'ML Complexity Predictor' not in modules_used:
                print_error("ML Complexity Predictor not listed in modules_used")
                return False
            
            print_success("ML Complexity Predictor listed in analysis metadata")
            
            # Print summary
            print("\n" + "-" * 70)
            print("Analysis Results Summary:")
            print("-" * 70)
            print(f"Language: {result.get('language')}")
            print(f"Quality Score: {result.get('quality_score', {}).get('overall_score', 'N/A')}")
            print(f"ML Complexity: {prediction.get('predicted_complexity', 'N/A')}")
            print(f"Technical Debt: {result.get('technical_debt', {}).get('total_debt_score', 'N/A')}")
            print(f"Code Smells: {result.get('code_smells', {}).get('total_smells', 0)}")
            
            return True
            
        finally:
            os.unlink(tmp_path)
            
    except Exception as e:
        print_error(f"Error testing analysis pipeline: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_api_structure():
    """Verify API response structure matches frontend expectations"""
    print_header("5. API Response Structure Verification")
    
    try:
        from feature_router import FeatureRouter
        
        router = FeatureRouter()
        
        # Create minimal test file
        test_code = "def test(): pass"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            tmp_path = f.name
        
        try:
            result = router.analyze_code(file_path=tmp_path)
            
            # Check structure matches what frontend expects
            frontend_expectations = {
                'analysisData.ml_complexity.prediction.complexity_description': 
                    result.get('ml_complexity', {}).get('prediction', {}).get('complexity_description'),
                'analysisData.quality_score.overall_score':
                    result.get('quality_score', {}).get('overall_score'),
                'analysisData.technical_debt.total_debt_score':
                    result.get('technical_debt', {}).get('total_debt_score'),
                'analysisData.code_smells.total_smells':
                    result.get('code_smells', {}).get('total_smells'),
            }
            
            all_present = True
            for path, value in frontend_expectations.items():
                if value is None:
                    print_error(f"Frontend expects {path} but it's missing")
                    all_present = False
                else:
                    print_success(f"{path} = {value}")
            
            return all_present
            
        finally:
            os.unlink(tmp_path)
            
    except Exception as e:
        print_error(f"Error verifying API structure: {e}")
        return False

def main():
    """Run all verification checks"""
    print("\n" + "=" * 70)
    print("  DevEase ML & Backend Verification Script")
    print("=" * 70)
    
    results = {
        "ML Model & Dataset": verify_ml_model(),
        "ML Prediction": verify_ml_prediction(),
        "Backend Modules": verify_backend_modules(),
        "Analysis Pipeline": verify_analysis_pipeline(),
        "API Structure": verify_api_structure(),
    }
    
    print_header("Verification Summary")
    
    all_passed = True
    for check_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {check_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print_success("ALL CHECKS PASSED - Your ML and backend are working correctly!")
        print("\nNext steps:")
        print("  1. Start backend: cd backend && python -m app.main")
        print("  2. Start frontend: cd frontend && npm run dev")
        print("  3. Upload a file and verify ML predictions appear in UI")
    else:
        print_error("SOME CHECKS FAILED - Please review errors above")
        print("\nCommon fixes:")
        print("  1. Train ML model: python -c \"from ml_complexity_predictor import ComplexityPredictor; p = ComplexityPredictor(); p.train_model('dataset1.csv', force_retrain=True)\"")
        print("  2. Check dataset1.csv exists in project root")
        print("  3. Verify all Python dependencies are installed: pip install -r requirements.txt")
    print("=" * 70 + "\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
