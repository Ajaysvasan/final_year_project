from typing import Dict, List, Tuple

from config import Config

from .HierarchicalChunker import HierarchicalChunker
from .normalised_content import NormalizedContent
from .RecursiveChunker import RecursiveChunker


class Chunker:
    def __init__(self, chunk_size=256, overlap=20, db_path=Config.DB_PATH):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.db_path = db_path

    #  NO returns as the values are stored in the Db
    def _call_hierarchical_chunker(self, hierarchical_chunker_list: List[Dict]) -> None:
        hierarchical_chunker = HierarchicalChunker(
            self.chunk_size, self.overlap, self.db_path, hierarchical_chunker_list
        )
        hierarchical_chunker.process_doc()

    def __call_recursive_chunker(self, recursive_chunker_list: List[Dict]):
        recursive_chunker = RecursiveChunker(
            recursive_chunker_list, self.chunk_size, self.overlap
        )
        return recursive_chunker.recursive_chunker()

    def __hierarchical_and_recursive_objects(
        self, normalised_content: List[NormalizedContent]
    ) -> Tuple[List[Dict], List[Dict]]:
        hierarchical_chunker_list: List[Dict] = []
        recursive_chunker_list: List[Dict] = []
        for content in normalised_content:
            if content.has_section:
                hierarchical_chunker_list.append(content.processed_file_information)
            else:
                recursive_chunker_list.append(content.processed_file_information)
        return hierarchical_chunker_list, recursive_chunker_list

    def __chunk_per_document(self, normalised_content: List[NormalizedContent]):
        hierarchical_chunker_list, recursive_chunker_list = (
            self.__hierarchical_and_recursive_objects(normalised_content)
        )
        self._call_hierarchical_chunker(hierarchical_chunker_list)
        r_chunks = self.__call_recursive_chunker(recursive_chunker_list)
