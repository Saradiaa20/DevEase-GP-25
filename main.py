import os
import shutil
from parsing import ASTParser
from file_handler import FileHandler

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
