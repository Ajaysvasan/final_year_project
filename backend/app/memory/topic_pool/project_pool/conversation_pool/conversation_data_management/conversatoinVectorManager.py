from typing import List, Union

import numpy as np
from memory_pool_exceptions import InvalidVectorDimension

from config import Config


class ConversationVectorManager:
    def __init__(
        self, vector_dimension=Config.DIMENSIONS, vector_dtype=Config.VECTOR_DTYPE
    ) -> None:
        self.path = (
            r"memory/topic_pool/project_pool/conversation_pool/conversation_vectors/"
        )
        self.vector_dimension = vector_dimension
        self.vector_dtype = vector_dtype

    def __validate_vectors(self, vector: np.ndarray):
        if vector.shape[0] != self.vector_dimension:
            raise InvalidVectorDimension(vector.shape[0], self.vector_dimension)
        if not isinstance(vector[0].dtype, self.vector_dtype):
            vector = vector.astype(self.vector_dtype)
        return vector

    def batch_add_vectors(self, project_id: str, vectors: List[np.ndarray]):
        pass

    def get_batch_vectors(self, indicies: List, project_id: str):
        pass
