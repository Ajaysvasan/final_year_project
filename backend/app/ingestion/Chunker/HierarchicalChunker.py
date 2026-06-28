import hashlib
import os
import re
import sys
from dataclasses import dataclass
from typing import List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from .DB_Manager import Manager


@dataclass(frozen=True)
class Document:
    documentId: str
    documentName: str


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


class HierarchicalChunker:
    documentName: str
    documentId: str
    normalizedText: str
    chunkOverlap: int
    chunkSize: int

    def __init__(
        self,
        chunkOverlap: int,
        documentName: str,
        documentId: str,
        normalizedText: str,
        chunkSize: int,
    ) -> None:
        self.chunkOverlap = chunkOverlap
        self.documentName = documentName
        self.documentId = documentId
        self.normalizedText = normalizedText
        self.chunkSize = chunkSize

    def __generate_id(self, value):
        hash_object = hashlib.sha256(value.encode("utf-8"))
        hex_digest = hash_object.hexdigest()
        return str(hex_digest)

    def __find_sections(self, doc: Document):

        sections: List[Section] = []
        pattern = re.compile(r"^[A-Z\s]+$", re.MULTILINE)
        matches = list(pattern.finditer(self.normalizedText))
        for i, match in enumerate(matches):
            sectionName = match.group().strip()
            sectionId = self.__generate_id(sectionName)
            headerStart = match.start()
            headerEnd = match.end()
            contentStart = headerEnd

            if i + 1 < len(matches):
                contentEnd = matches[i + 1].start()
            else:
                contentEnd = len(self.normalizedText)

            content = self.normalizedText[contentStart:contentEnd].strip()
            sectionObj = Section(
                sectionId,
                doc.documentId,
                sectionName,
                content,
                len(content),
                headerStart,
                headerEnd,
            )
            sections.append(sectionObj)
        return sections

    def __make_document_obj(self):
        return Document(self.documentId, self.documentName)

    def __find_contexts(self, sections: List[Section]) -> List[Context]:
        contexts: List[Context] = []
        for section in sections:
            content = section.content
            pattern = re.compile(r"\n\s*\n")
            matches = list(pattern.finditer(content))

            start_idx = 0  # Start tracking from the beginning of the section

            for match in matches:
                # The paragraph ends where the double newline starts
                end_idx = match.start()
                context_text = content[start_idx:end_idx].strip()

                if context_text:  # Only add if it's not an empty string
                    contextId = self.__generate_id(context_text)
                    contextObj = Context(
                        contextId=contextId,
                        sectionId=section.sectionId,
                        context=context_text,
                        contextLen=len(context_text),
                        startOffSet=start_idx,
                        endOffSet=end_idx,
                    )
                    contexts.append(contextObj)

                # Update the start index for the NEXT paragraph to be after the current double newline
                start_idx = match.end()

            # Capture the final paragraph after the last double newline
            if start_idx < len(content):
                context_text = content[start_idx:].strip()
                if context_text:
                    contextId = self.__generate_id(context_text)
                    contextObj = Context(
                        contextId=contextId,
                        sectionId=section.sectionId,
                        context=context_text,
                        contextLen=len(context_text),
                        startOffSet=start_idx,
                        endOffSet=len(content),
                    )
                    contexts.append(contextObj)
        return contexts

    def __get_chunks(self, contexts: List[Context]) -> List[Chunk]:
        if self.chunkOverlap >= self.chunkSize:
            raise ValueError(
                "Invalid chunk overlap and chunk size. chunkSize must be greater than chunkOverlap"
            )

        chunks: List[Chunk] = []

        for context in contexts:
            start = 0
            while start < len(context.context):
                end = min(start + self.chunkSize, len(context.context))
                chunk = context.context[start:end]
                chunkId = self.__generate_id(chunk)
                chunkObj = Chunk(chunkId, context.contextId, chunk, start, end)
                start += self.chunkSize - self.chunkOverlap
                chunks.append(chunkObj)
        return chunks

    def chunk_text(self):
        doc = self.__make_document_obj()
        sections = self.__find_sections(doc)
        contexts = self.__find_contexts(sections)
        chunks = self.__get_chunks(contexts)
        return chunks
