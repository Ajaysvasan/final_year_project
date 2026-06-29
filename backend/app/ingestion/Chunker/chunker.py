import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from HierarchicalChunker import HierarchicalChunker

from .DB_Manager import Manager


class Chunker:
    def __init__(self, chunk_size=256):
        self.chunk_size = chunk_size
