from dataclasses import dataclass
from drafter import *

@dataclass
class State:
    student_name: str
    test_scores: list[float]
    target_GPA: float


# start_server()