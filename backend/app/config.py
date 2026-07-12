import os
from pathlib import Path

import numpy as np


class Config:
    """
    Configuration class for the backend application.
    Modify or extend these attributes as needed for your final year project.
    """

    APP_NAME = "Final Year Project Backend"
    DATASET_PATH = Path("dataset").resolve().parent / "dataset"
    DEBUG = False
    LOG_FILE = "log/app.log"
    ABS_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(ABS_PATH, "data")
    DB_PATH = "hierarchical_db"
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    MODEL_PATH = None
    INDEX_PATH = "./disk_ann_index"
    DISTANCE_METRIC = "l2"
    VECTOR_DTYPE = np.float32
    DIMENSIONS = 128
    MAX_VECTORS = 1000000
    COMPLEXITY = 100
    GRPAH_DEGREE = 120
    NUM_THREADS = 4
    K_NEIGHBORS = 9
    CONVERSATION_SNAPSHOT_DB = (
        "memory/topic_pool/project_pool/conversation_pool/conversation_snapshot.db"
    )


config = Config()
