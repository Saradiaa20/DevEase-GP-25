import os
import shutil
import sys
from parsing import ASTParser
# from file_handler import FileHandler, analyze_file


class FileHandler:
    SUPPORTED_EXTENSIONS = ['.java', '.py', '.js', '.cpp', '.cs', '.php']
    
    def __init__(self, storage_folder="project_files"):
        self.storage_folder = storage_folder
        self._ensure_storage_folder()

    def _ensure_storage_folder(self):
        os.makedirs(self.storage_folder, exist_ok=True)

    def user_input_file(self):
        file_path = input("Enter the full path of the code file: ").strip()
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        _, ext = os.path.splitext(file_path)
        if ext.lower() not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {ext}")
        return file_path

    def read_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    def save_to_local_folder(self, source_path):
        filename = os.path.basename(source_path)
        destination = os.path.join(self.storage_folder, filename)
        shutil.copy(source_path, destination)
        print(f"File saved to local folder: {destination}")
        return destination

    def get_saved_path(self, filename):
        file_path = os.path.join(self.storage_folder, filename)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"No such file saved: {filename}")
        return file_path


def analyze_file(file_path, handler, parser):
    """Complete analysis workflow: File Handler → Parsing → Code Smell Detection"""
    try:
        # Step 1: File Handler - Validate and read file
        # print(f"\nFile Handler: Processing {file_path}")
        # print("-" * 50)
        
        if not os.path.exists(file_path):
            print(f"ERROR: File not found: {file_path}")
            return False
        
        _, ext = os.path.splitext(file_path)
        if ext.lower() not in handler.SUPPORTED_EXTENSIONS:
            print(f"ERROR: Unsupported file type: {ext}")
            print(f"Supported types: {', '.join(handler.SUPPORTED_EXTENSIONS)}")
            return False
        
        # Read file content
        content = handler.read_file(file_path)
        # print(f"SUCCESS: File loaded successfully ({len(content)} characters)")
        
        # Step 2: Parsing - AST Analysis
        # print("\nParsing: AST Analysis")
        # print("-" * 50)
        
        result = parser.parse_file(file_path)
        
        # Display AST results
        print("\nParsing: AST Analysis")
        print("-" * 50)
        for k, v in result.items():
            if k not in ["code_smells", "quality_score"]:
                if isinstance(v, list) and len(v) > 10:
                    print(f"{k}: {len(v)} items - {v[:5]}... (showing first 5)")
                else:
                    print(f"{k}: {v}")
        
        # Step 3: Code Smell Detection
        print("\nCode Smell Detection: Analyzing code quality")
        print("-" * 50)
        
        if "code_smells" in result:
            parser.smell_detector.print_smell_report()
        
        # Step 4: Quality Metrics
        # print("\nCode Quality Metrics: Overall assessment")
        # print("-" * 50)
        
        if "quality_score" in result:
            parser.quality_analyzer.print_quality_report(result["quality_score"])
        
        # Step 5: ML Complexity Prediction
        # print("\nML Complexity Prediction: AI-powered analysis")
        print("-" * 50)
        
        if "ml_complexity" in result:
            ml_data = result["ml_complexity"]
            if "error" not in ml_data:
                print("Extracted Features:")
                for feature, value in ml_data["features"].items():
                    print(f"  {feature}: {value}")
                
                # print("\nML Prediction Results:")
                # if "prediction" in ml_data and "error" not in ml_data["prediction"]:
                #     parser.complexity_predictor.print_prediction_report(ml_data["prediction"])
                # else:
                #     print("  No trained model available. Train the model first!")
            else:
                print(f"ML Prediction Error: {ml_data['error']}")
        
        print("\n" + "-" * 50)
        print("SUCCESS: Complete Analysis Finished Successfully!")

        
        return True
        
    except Exception as e:
        print(f"ERROR: Error during analysis: {e}")
        return False

def main():
    """Main DevEase application with corrected logic"""
    print("-" * 60)
    print("    DevEase - Code Quality Analysis Tool")
    print("-" * 60)
    print()
    
    # Initialize components
    handler = FileHandler()
    parser = ASTParser()
    
    # Auto-train ML model on startup
    dataset_path = os.path.join(os.path.dirname(__file__), "dataset1.csv")
    
    if os.path.exists(dataset_path):
        print("Training ML model for complexity prediction...")
        parser.complexity_predictor.verify_preprocessing(dataset_path)
        success = parser.complexity_predictor.train_model(dataset_path, force_retrain=True)
        
        if success:
            print("Model trained successfully.\n")
        else:
            print("WARNING: ML model training failed, but system will continue...\n")
    else:
        print(f"WARNING: Dataset not found at {dataset_path}")
        print("ML complexity prediction will not be available.\n")
    
    # Main interactive loop
    while True:
        print("-" * 50)
        print("\nWelcome to DevEase")
        print("1. Upload a new file")
        print("2. Choose a saved file")
        print("3. Exit")
        
        try:
            choice = input("\nEnter choice: ").strip()
            
            if choice == "1":
                # Upload and analyze new file
                file_path = input("Enter the full path of the code file: ").strip()
                
                if not file_path:
                    print("ERROR: No file path provided!")
                    continue
                
                # Perform complete analysis using the analyze_file function
                success = analyze_file(file_path, handler, parser)
                
                if success:
                    # Ask if user wants to save the file
                    save = input("\nSave this file locally? (y/n): ").lower()
                    if save == 'y':
                        try:
                            handler.save_to_local_folder(file_path)
                            print("File saved successfully!")
                        except Exception as e:
                            print(f"Error saving file: {e}")
            
            elif choice == "2":
                # Choose from saved files
                files = os.listdir(handler.storage_folder)
                if not files:
                    print("\nERROR: No saved files found!")
                    continue 
                
                print("\nSaved files:")
                for i, file in enumerate(files, 1):
                    print(f"{i}. {file}")
                
                try:
                    idx = int(input("\nChoose file number: ")) - 1
                    if 0 <= idx < len(files):
                        selected_file = files[idx]
                        file_path = handler.get_saved_path(selected_file)
                        
                        # Perform complete analysis
                        analyze_file(file_path, handler, parser)
                    else:
                        print("ERROR: Invalid file number!")
                except ValueError:
                    print("ERROR: Please enter a valid number!")
            
            elif choice == "3":
                print("\nThank you for using DevEase.")
                break
            
            else:
                print("ERROR: Invalid choice! Please enter 1, 2, or 3.")
        
        except KeyboardInterrupt:
            print("\n\nExiting DevEase. Goodbye!")
            break  
        except FileNotFoundError as e:
            print(f"ERROR: {e}")
        except Exception as e:
            print(f"ERROR: An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()