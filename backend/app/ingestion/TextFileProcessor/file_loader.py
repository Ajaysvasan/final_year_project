import os
from pathlib import Path
from typing import Dict, List


class FileLoader:
    def __init__(self, folder_path: str):
        self.folder_path = folder_path
        self.allowed_extensions = {
            ".doc",
            ".docx",
            ".txt",
            ".pdf",
            ".csv",
            ".md",
            ".html",
            ".xml",
        }

    def __is_directory(self, path: str) -> bool:
        return os.path.isdir(path)

    def __get_file_category(self, file_name: str) -> str:
        extension = Path(file_name).suffix.lower()
        if extension in self.allowed_extensions:
            return extension[1:]
        return "unknown"

    def __scan_directory(self, path: str, loaded_files: Dict[str, List[Path]]) -> None:
        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)

                if self.__is_directory(item_path):
                    self.__scan_directory(item_path, loaded_files)
                else:
                    category = self.__get_file_category(item_path)
                    if category != "unknown":
                        if category not in loaded_files:
                            loaded_files[category] = []
                        loaded_files[category].append(Path(item_path))

        except PermissionError:
            print(f"Permission denied: {path}")
        except Exception as e:
            print(f"Error scanning directory {path}: {e}")

    def load_files(self) -> Dict[str, List[Path]]:
        if not os.path.exists(self.folder_path):
            raise ValueError(f"The provided path '{self.folder_path}' does not exist.")
        if not self.__is_directory(self.folder_path):
            raise ValueError(
                f"The provided path '{self.folder_path}' is not a directory."
            )

        loaded_files = {ext[1:]: [] for ext in self.allowed_extensions}

        self.__scan_directory(self.folder_path, loaded_files)
        return loaded_files


if __name__ == "__main__":
    folder_path = "folde/path"
    file_loader = FileLoader(folder_path)

    try:
        files = file_loader.load_files()
        for category, file_list in files.items():
            print(f"{category}: {len(file_list)} files found")
    except ValueError as e:
        print(e)
