from typing import List
from warnings import warn

from ingestion_exceptions.ingestion_exceptions import IndexDirectoryDoesNotExists
from vectorDB_diskann import VectorDb_diskann as vdap

from config import Config

from ..nodes.nodes import EmbeddedChunk


class VectorDbManager:
    def __init__(
        self,
        distance_metrics: str,
        vector_dtype: int,
        dimensions: int,
        max_vectors: int,
        complexity: int,
        graph_degree: int,
        num_threads: int,
        k_neighbors: int,
    ) -> None:
        self.distance_metrics = distance_metrics
        self.vector_dtype = vector_dtype
        self.dimensions = dimensions
        self.max_vectors = max_vectors
        self.complexity = complexity
        self.graph_degree = graph_degree
        self.num_threads = num_threads
        self.k_neighbors = k_neighbors
        self.vector_db = vdap(
            self.distance_metrics,
            self.vector_dtype,
            self.dimensions,
            self.max_vectors,
            self.complexity,
            self.graph_degree,
            self.num_threads,
        )

    def __insert_vector(self, vector, vector_id) -> None:
        self.vector_db.insert(vector, vector_id)

    def __insert_vectors_in_batch(self, vectors, vector_ids) -> None:
        self.vector_db.batch_insert(vectors, vector_ids)

    def insert(self, embedded_chunk_obj: EmbeddedChunk) -> None:
        vector = embedded_chunk_obj.vector
        vector_id = embedded_chunk_obj.meta_data.chunk_id
        self.__insert_vector(vector, vector_id)

    def batch_insert(self, embedded_chunk_objs: List[EmbeddedChunk]):
        vectors = []
        vector_ids = []
        for embedded_chunk_obj in embedded_chunk_objs:
            vectors.append(embedded_chunk_obj.vector)
            vector_ids.append(embedded_chunk_obj.meta_data.chunk_id)
        self.__insert_vectors_in_batch(vectors, vector_ids)

    def search_vector(self, query):
        return self.vector_db.search_vector(query, self.k_neighbors, self.complexity)

    def batch_search_vectors(self, queries):
        return self.vector_db.batch_search_vector(
            queries, self.k_neighbors, self.complexity
        )

    def delete_vector(self, vector_id) -> None:

        self.vector_db.delete_vector(vector_id)

    def delete_vectors(self, vector_ids) -> None:
        self.vector_db.delete_vectors(vector_ids)

    def save(self, save_path=Config.INDEX_PATH):
        self.vector_db.save(save_path)

    def load(self, load_path=Config.INDEX_PATH):
        try:
            return self.vector_db.load(load_path)
        except IndexDirectoryDoesNotExists:
            warn(
                f"No directory {load_path} exists , please ensure to enter in the correct path. Returning None"
            )
            return None
