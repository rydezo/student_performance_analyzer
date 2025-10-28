from dataclasses import dataclass
from drafter import *

@dataclass
class Course:
    course_name: str
    current_grade: float
    test_scores: list[float]

@dataclass
class State:
    # add welcome message
    student_name: str
    target_GPA: float
    current_GPA: float
    courses = list[Course]

@route
def index(state: State):
    return Page(
        state,
        content=[
            # add welcome message
            Header(f"Welcome, {state.student_name}")]
    )


# start_server()