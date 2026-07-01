from dataclasses import dataclass
from typing import Any, Dict, List

from ingestion.metadata import (
    ChunkMetaData,
    EmbeddedChunkMetaData,
    NormalizedTextMetaData,
)


@dataclass(frozen=True)
class Document:
    documentId: str
    documentName: str
    normalizedText: str
    meta_data: None


@dataclass(frozen=True)
class Section:
    sectionId: str
    documentId: str

    sectionName: str
    content: str
    contentLength: int

    startOffSet: int
    endOffSet: int

    meta_data: None


@dataclass(frozen=True)
class Context:
    contextId: str
    sectionId: str

    context: str
    contextLen: int

    startOffSet: int
    endOffSet: int
    meta_data: None


@dataclass(frozen=True)
class Chunk:
    chunkId: str
    contextId: str

    chunk: str

    startOffSet: int
    endOffSet: int
    meta_data: ChunkMetaData


@dataclass
class NormalizedContent:
    has_section: bool
    meta_data: NormalizedTextMetaData


@dataclass(frozen=True)
class EmbeddedChunk:
    vector: Any[float]
    meta_data: EmbeddedChunkMetaData
