from dataclasses import dataclass
from drafter import *

@dataclass
class Course:
    course_name: str
    credits: int
    # convert to letter grade when displaying to user
    current_grade: float
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
            Header(f"Welcome, {state.student_name}"),
            f"Your GPA: {state.current_GPA}",
            Button("Add Course", "/add_course"),
            Button("Remove Course", "/remove_course"),
            Button("View Courses", "/view_courses"),
            Button("Add Test Score", "/add_test_score"),
            Button("View Progress", "/view_progress")]
    )

@route
def add_course(state: State) -> Page:
    pass

@route
def remove_course(state: State) -> Page:
    pass

@route
def view_courses(state: State) -> Page:
    pass

@route
def add_test_score(state: State) -> Page:
    pass

@route
def view_progress(state: State) -> Page:
    pass


start_server(State("test name", 4.0, 3.5, False, [], []))