import os
import sys


class Chunker:
    def __init__(self, chunk_size=1000):
        self.chunk_size = chunk_size
