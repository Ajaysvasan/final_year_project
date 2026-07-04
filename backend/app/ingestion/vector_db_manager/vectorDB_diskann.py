import diskannpy as dann

from config import Config


class VectorInsertionError(Exception):
    def __init__(self, vector_id):
        self.vector_id = vector_id
        super().__init__(self.vector_id)

    def __str__(self):
        return f"An Error occured while inserting the vector : {self.vector_id}"


class VectorDb_diskann:
    def __init__(
        self,
        distance_metrics: str,
        vector_dtype,
        dimensions: int,
        max_vectors: int,
        complexity: int,
        graph_degree: int,
        num_threads: int,
    ):
        self.distance_metrics = distance_metrics
        self.vector_dtype = vector_dtype
        self.dimensions = dimensions
        self.max_vectors = max_vectors
        self.complexity = complexity
        self.graph_degree = graph_degree
        self.num_threads = num_threads
        self.dynamic_dann = dann.DynamicMemoryIndex(
            distance_metric=self.distance_metrics,
            vector_dtype=self.vector_dtype,
            dimensions=self.dimensions,
            max_vectors=self.max_vectors,
            graph_degree=self.graph_degree,
            search_threads=self.num_threads,
            complexity=self.complexity,
        )

    def __insert_vector(self, vector, vector_id):
        try:
            self.dynamic_dann.insert(vector, vector_id)
        except:
            raise VectorInsertionError(vector_id)

    def __insert_vectors(self, vectors, vector_ids):
        self.dynamic_dann.batch_insert(vectors, vector_ids)

    def __delete(self, vector_id):
        self.dynamic_dann.mark_deleted(vector_id)

    def __delete_all(self, vector_ids):
        for vector_id in vector_ids:
            self.__delete(vector_id)

    def delete(self, id, is_delete_all):
        if is_delete_all:
            self.__delete_all(id)
        else:
            self.__delete(id)
        self.dynamic_dann.consolidate_delete()

    def insert(self, data, id, is_batch: bool):
        if is_batch:
            self.__insert_vectors(data, id)
        else:
            self.__insert_vector(data, id)

        print("Insertion done")

    def __search_vector(self, query, k_neighbors, complexity):
        pass

    def __batch_search_vector(self):
        pass

    def search(self, id):
        pass

    def save(self, save_path=Config.INDEX_PATH):
        self.dynamic_dann.save(save_path)

    def load(self, load_path=Config.INDEX_PATH):
        return self.dynamic_dann.from_file(
            index_directory=load_path,
            max_vectors=self.max_vectors,
            complexity=self.complexity,
            graph_degree=self.graph_degree,
            search_threads=self.num_threads,
            distance_metric=self.distance_metrics,
            vector_dtype=self.vector_dtype,
            dimensions=self.dimensions,
        )
