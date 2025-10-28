from dataclasses import dataclass
from drafter import *

@dataclass
class State:
    # add welcome message
    student_name: str
    test_scores: list[float]
    target_GPA: float

@route
def index(state: State):
    return Page(
        state,
        content=[
            # add welcome message
            Header(f"Welcome, {state.student_name}")]
    )


# start_server()