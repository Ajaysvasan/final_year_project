from typing import List

from sentence_transformers import SentenceTransformer

from config import Config
from ingestion.metadata import EmbeddedChunkMetaData
from ingestion.nodes import EmbeddedChunk, HChunk, RChunk


class InvalidEmbeddingArgument(Exception):
    def __init__(self, error_message) -> None:
        self.error_message = error_message
        super().__init__(error_message)

    def __str__(self):
        return self.error_message


class EmbeddingManager:
    def __init__(self, model_name: str = Config.EMBEDDING_MODEL):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def __create_meta_data(self, chunk_id: str, chunk: str) -> EmbeddedChunkMetaData:
        return EmbeddedChunkMetaData(chunk_id, chunk, self.model_name)

    def __embed_chunk(self, chunkObj: HChunk | RChunk) -> EmbeddedChunk:
        chunk = chunkObj.chunk
        chunk_id = chunkObj.chunk_id
        embedded_chunk = self.model.encode(chunk)
        return EmbeddedChunk(
            embedded_chunk.tolist(), self.__create_meta_data(chunk_id, chunk)
        )

    def __embed_chunks(self, chunks: List[HChunk | RChunk]) -> List[EmbeddedChunk]:
        embedded_chunks: List[EmbeddedChunk] = []
        texts = []
        for chunkObj in chunks:
            if not isinstance(chunkObj, HChunk | RChunk):
                raise InvalidEmbeddingArgument(
                    f"The argument passed is of type {type(chunkObj).__name__}. The valid types are Chunk and list"
                )
            texts.append(chunkObj.chunk)
        vectors = self.model.encode(texts)
        for chunkObj, vector in zip(chunks, vectors):
            chunk = chunkObj.chunk
            chunk_id = chunkObj.chunk_id
            embedded_chunks.append(
                EmbeddedChunk(vector.tolist(), self.__create_meta_data(chunk_id, chunk))
            )
        return embedded_chunks

    def embed(
        self, arg: HChunk | RChunk | List[HChunk | RChunk]
    ) -> EmbeddedChunk | List[EmbeddedChunk]:
        if isinstance(arg, HChunk | RChunk):
            return self.__embed_chunk(arg)
        if isinstance(arg, list):
            return self.__embed_chunks(arg)
        raise InvalidEmbeddingArgument(
            f"The argument passed is of type {type(arg).__name__}. The valid types are Chunk and List[Chunk]"
        )
