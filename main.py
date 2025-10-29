from dataclasses import dataclass
from drafter import *

@dataclass
class Course:
    course_name: str
    # convert to letter grade when displaying to user
    current_grade: float
    credits: int
    test_scores: list[float]

@dataclass
class State:
    student_name: str
    target_GPA: float
    current_GPA: float
    is_failing: bool
    courses: list[Course]
    threshold_test_scores: list[int]

@route
def index(state: State) -> Page:
    return Page(
        state,
        content=[
            # add welcome message
            Header(f"Welcome, {state.student_name}")]
    )

@route
def add_course(state: State) -> Page:
    pass

@route
def remove_course(state: State) -> Page:
    pass


# start_server()