import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

print(f"Config.DATASET_PATH: {Config.DATASET_PATH}")
