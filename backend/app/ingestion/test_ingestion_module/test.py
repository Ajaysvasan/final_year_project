import numpy as np

from config import Config
from ingestion.vector_db_manager.vectorDB_diskann import VectorDb_diskann as vdap

# 10,000 vectors with 128 dimensions each (Float32)
num_vectors = 10000
dimensions = 128
data = np.random.randn(num_vectors, dimensions).astype(np.float32)

id = np.arange(1, 10001, dtype=np.uint32)

dann = vdap(
    distance_metrics="l2",
    vector_dtype=np.float32,
    dimensions=dimensions,
    max_vectors=20000,
    complexity=100,
    graph_degree=120,
    num_threads=2,
)

dann.insert(data, id, is_batch=True)
