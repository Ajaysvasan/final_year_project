from dataclasses import dataclass
from typing import List

from numpy import uint32


@dataclass(frozen=True)
class SnapShotNode:
    time_of_snap_shot: str

    size_of_the_summary: int

    len_of_the_summary: int

    summary_index: int

    summary_vector_ids: List[uint32]

    conversation_id: str

    cummulative_summary_vector_id: uint32
