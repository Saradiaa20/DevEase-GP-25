import os
import shutil

class FileHandler:
    """
    Handles reading, writing, saving, and retrieving user code files.
    Supports multiple languages (Java, Python, JS, etc.)
    """

    SUPPORTED_EXTENSIONS = ['.java', '.py', '.js', '.cpp', '.cs', '.php']
    
    def __init__(self, storage_folder="project_files"):
        self.storage_folder = storage_folder
        self._ensure_storage_folder()

    def _ensure_storage_folder(self):
        """Create the storage folder if it doesn't exist."""
        os.makedirs(self.storage_folder, exist_ok=True)

    def user_input_file(self):
        """Prompt user to enter a file path for reading/writing."""
        file_path = input("Enter the full path of the code file: ").strip()
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        _, ext = os.path.splitext(file_path)
        if ext.lower() not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {ext}")
        return file_path

    def read_file(self, file_path):
        """Read and return the content of the file."""
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        print(f"\nSuccessfully read: {file_path}")
        return content

    def save_to_local_folder(self, source_path):
        """Copy uploaded file into the storage folder for future use."""
        filename = os.path.basename(source_path)
        destination = os.path.join(self.storage_folder, filename)
        shutil.copy(source_path, destination)
        print(f"File saved to local folder: {destination}")
        return destination

    def get_saved_path(self, filename):
        """Retrieve full path to a saved file."""
        file_path = os.path.join(self.storage_folder, filename)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"No such file saved: {filename}")
        return file_path


# ----------------- MAIN PROGRAM LOOP -----------------
if __name__ == "__main__":
    handler = FileHandler()

    while True:
        print("\n Welcome to DevEase")
        print("1. Upload a new file")
        print("2. Read from saved files")
        print("3. Exit")
        choice = input("\nEnter your choice (1, 2, or 3): ").strip()

        try:
            match choice:
                # Option 1: Upload a new file
                case "1":
                    try:
                        path = handler.user_input_file()
                        content = handler.read_file(path)
                        print("\n--- File Content Preview ---\n")
                        print(content[:300])  # preview first 300 characters
                        
                        save_choice = input("\nDo you want to save this file to your local folder? (y/n): ").lower()
                        if save_choice == 'y':
                            handler.save_to_local_folder(path)

                    except (FileNotFoundError, ValueError) as e:
                        print(f"\n{e}")

                # Option 2: Read from saved files
                case "2":
                    files = os.listdir(handler.storage_folder)

                    # If no saved files exist, prompt user to upload
                    if not files:
                        print("\nNo saved files found. Please upload a file first.")
                        upload_now = input("Do you want to upload one now? (y/n): ").lower()
                        if upload_now == 'y':
                            path = handler.user_input_file()
                            content = handler.read_file(path)
                            handler.save_to_local_folder(path)
                        else:
                            continue  # return to main menu
                    else:
                        print("\nSaved files:")
                        for i, file in enumerate(files, 1):
                            print(f"{i}. {file}")

                        file_choice = input("\nEnter the number of the file you want to open: ").strip()
                        if not file_choice.isdigit() or int(file_choice) not in range(1, len(files) + 1):
                            print("Invalid choice. Please try again.")
                            continue

                        selected_file = files[int(file_choice) - 1]
                        selected_path = handler.get_saved_path(selected_file)
                        content = handler.read_file(selected_path)
                        print("\n--- File Content Preview ---\n")
                        print(content[:300])

                # Option 3: Exit
                case "3":
                    print("\nExit system successfully.")
                    break

                # Invalid input
                case _:
                    print("Invalid option. Please enter 1, 2, or 3.")

        except Exception as e:
            print(f"\nUnexpected error: {e}")
