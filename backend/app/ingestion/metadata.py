from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class NormalizedTextMetaData:
    document_id: str
    file_name: str
    file_type: str
    ingestion_time: str
    normalizer_version: str
    content_hash: str
    source_path: str | None = None


@dataclass(frozen=True)
class ChunkMetaData:
    document_name: str
    document_id: str
    chunking_algorithm_used: str


@dataclass(frozen=True)
class EmbeddedChunkMetaData:
    chunk_id: str
    chunk: str
    modelUsedForChunking: str
