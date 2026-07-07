from enum import Enum


class ChunkingAlgorithmType(str, Enum):
    HIERARCHICAL = "hierarchical"
    RECURSIVE = "recursive"
