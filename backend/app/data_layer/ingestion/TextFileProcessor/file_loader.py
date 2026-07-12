import os
from pathlib import Path
from typing import Dict, List

from config import get_logger

logger = get_logger(__name__)


class FileLoader:
    def __init__(self):
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
                    else:
                        logger.debug(f"Ignored unsupported file extension during directory scan: '{item_path}'")

        except PermissionError:
            logger.error(f"Permission denied while scanning directory: '{path}'")
        except Exception as e:
            logger.error(f"Error scanning directory '{path}': {e}", exc_info=True)

    def load_files(self, folder_path) -> Dict[str, List[Path]]:
        if not os.path.exists(folder_path):
            logger.error(f"load_files failed: path '{folder_path}' does not exist.")
            raise ValueError(f"The provided path '{folder_path}' does not exist.")
        if not self.__is_directory(folder_path):
            logger.error(f"load_files failed: path '{folder_path}' is not a directory.")
            raise ValueError(f"The provided path '{folder_path}' is not a directory.")

        logger.info(f"Scanning directory '{folder_path}' for allowed file extensions...")
        loaded_files = {ext[1:]: [] for ext in self.allowed_extensions}

        self.__scan_directory(folder_path, loaded_files)
        total_loaded = sum(len(files) for files in loaded_files.values())
        logger.info(f"Successfully loaded {total_loaded} file(s) across {len(loaded_files)} file categories from '{folder_path}'.")
        return loaded_files
