from dataclasses import dataclass


@dataclass(frozen=True)
class Document:
    documentId: str
    documentName: str
    normalizedText: str


@dataclass(frozen=True)
class Section:
    sectionId: str
    documentId: str

    sectionName: str
    content: str
    contentLength: int

    startOffSet: int
    endOffSet: int


@dataclass(frozen=True)
class Context:
    contextId: str
    sectionId: str

    context: str
    contextLen: int

    startOffSet: int
    endOffSet: int


@dataclass(frozen=True)
class Chunk:
    chunkId: str
    contextId: str

    chunk: str

    startOffSet: int
    endOffSet: int
