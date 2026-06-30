from dataclasses import dataclass
from typing import Dict


@dataclass
class NormalizedContent:
    processed_file_information: Dict
    has_section: bool
