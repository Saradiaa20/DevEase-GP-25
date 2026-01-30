#!/usr/bin/env python3
"""
Fix ML Model Version Mismatch
Retrains the ML model using the current scikit-learn version to ensure compatibility.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    print("=" * 70)
    print("  Fixing ML Model Version Mismatch")
    print("=" * 70)
    print()
    
    # Check current scikit-learn version
    try:
        import sklearn
        print(f"Current scikit-learn version: {sklearn.__version__}")
    except ImportError:
        print("ERROR: scikit-learn not installed!")
        return 1
    
    # Check if dataset exists
    dataset_path = project_root / "dataset1.csv"
    if not dataset_path.exists():
        print(f"ERROR: Dataset not found at {dataset_path}")
        print("Cannot retrain model without dataset.")
        return 1
    
    print(f"Dataset found: {dataset_path}")
    print()
    
    # Import and train
    try:
        from ml_complexity_predictor import ComplexityPredictor
        
        print("Initializing ComplexityPredictor...")
        predictor = ComplexityPredictor()
        
        print("Training model with current scikit-learn version...")
        print("(This may take a few moments...)")
        print()
        
        success = predictor.train_model(str(dataset_path), force_retrain=True)
        
        if success:
            print()
            print("=" * 70)
            print("  ✓ SUCCESS: Model retrained successfully!")
            print("=" * 70)
            print()
            print("The ML model has been retrained and saved with scikit-learn")
            print(f"version {sklearn.__version__}.")
            print()
            print("Next steps:")
            print("  1. Run verify_ml_backend.py again - warnings should be gone")
            print("  2. Start your backend: cd backend && python -m app.main")
            print("  3. Test file uploads - predictions should now be accurate")
            return 0
        else:
            print()
            print("=" * 70)
            print("  ✗ ERROR: Model training failed")
            print("=" * 70)
            print()
            print("Please check the error messages above for details.")
            return 1
            
    except Exception as e:
        print()
        print("=" * 70)
        print("  ✗ ERROR: Failed to retrain model")
        print("=" * 70)
        print()
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
