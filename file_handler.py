import os
import shutil
from parsing import ASTParser

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


if __name__ == "__main__":
    handler = FileHandler()
    parser = ASTParser()

    while True:
        print("\n Welcome to DevEase ")
        print("1. Upload a new file")
        print("2. Choose a saved file")
        print("3. Exit")

        choice = input("\nEnter choice: ").strip()

        try:
            match choice:
                case "1":
                    path = handler.user_input_file()
                    handler.read_file(path)
                    save = input("Save this file locally? (y/n): ").lower()
                    if save == 'y':
                        handler.save_to_local_folder(path)

                    print("\n Parsing File using AST")
                    result = parser.parse_file(path)
                    for k, v in result.items():
                        print(f"{k}: {v}")
                    print("\n Exit System Scussefully.")
                    break

                case "2":
                    files = os.listdir(handler.storage_folder)
                    if not files:
                        print("\nNo saved files found!")
                        break

                    print("\nSaved files:")
                    for i, file in enumerate(files, 1):
                        print(f"{i}. {file}")
                    idx = int(input("\nChoose file number: ")) - 1
                    selected_file = files[idx]
                    file_path = handler.get_saved_path(selected_file)

                    print("\n Parsing File using AST")
                    result = parser.parse_file(file_path)
                    for k, v in result.items():
                        print(f"{k}: {v}")
                    print("\n Exit System Scussefully.")
                    break

                case "3":
                    print("\n Exit System Scussefully.")
                    break

                case _:
                    print("Invalid choice!")

        except Exception as e:
            print(f"Error: {e}")
            break
