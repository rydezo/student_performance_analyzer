from dataclasses import dataclass
from bakery import assert_equal
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
    current_GPA: float
    target_GPA: float
    is_failing: bool
    courses: list[Course]
    threshold_test_scores: list[int]

# page 1
@route
def index(state: State) -> Page:
    return Page(
        state,
        content=[
            # add welcome message
            Header(f"Welcome, {state.student_name}."),
            f"Your GPA: {state.current_GPA}",
            Button("Add Course", "/add_course"),
            Button("Remove Course", "/remove_course"),
            Button("View Courses", "/view_courses"),
            Button("Add Test Score", "/add_test_score"),
            Button("View Progress", "/view_progress")]
    )

# page 2
@route
def add_course(state: State) -> Page:
    return Page(
        state,
        content=[
            "Name of Course:", TextBox(name="course_name"),
            "Number of Credits:", TextBox(name="credits", default_value=3),
            "Current Grade:", TextBox(name="current_grade", default_value=100.0),
            Button(text="Add Course", url="/append_course"),
            Button(text="Cancel", url="/index")
        ]
    )

# route 7
@route
def append_course(state: State, course_name: str, credits: int, current_grade: float) -> Page:
    new_course = Course(course_name, credits, current_grade, [])
    state.courses.append(new_course)
    return index(state)

# page 3
@route
def remove_course(state: State) -> Page:
    return Page(
        state,
        content=[
            "Name of Course:", TextBox(name="course_name"),
            Button(text="Remove Course", url="/delete_course"),
            Button(text="Cancel", url="/index")
        ]
    )

@route
def delete_course(state: State, course_name: str) -> Page:
    for course in state.courses:
        if course.course_name == course_name:
            state.courses.remove(course)
    return index(state)

# page 4
@route
def view_courses(state: State) -> Page:
    if not state.courses:
        return Page(
            state,
            content=["You currently have no courses added. Please add some to view them.",
             Button("Add Course", "/add_course"),
             Button("Go to Home", "/index")]
        )
    else:
        course_names: list[str] = []
        course_credits: list[int] = []
        course_grades: list[float] = []
        course_test_scores: list[list[float]] = []

        for course in state.courses:
            course_names.append(course.course_name)
            course_credits.append(course.credits)
            course_grades.append(course.current_grade)
            course_test_scores.append(f"{course.course_name} scores: {course.test_scores}")
            
        return Page(
            state,
            content=[f"Courses: {course_names}",
                     f"Credits: {course_credits}",
                     f"Grades: {course_grades}",
                     f"Test Scores: {course_test_scores}",
                     Button("Go to Home", "/index")]
        )
    
    # display courses here

# page 5
@route
def add_test_score(state: State) -> Page:
    pass

# page 6
@route
def view_progress(state: State) -> Page:
    if state.is_failing:
        pass_status = "failing"
    else:
        pass_status = "passing"
    return Page(
        state,
        content=[f"Your GPA is {state.current_GPA}.",
            f"You are currently {pass_status}.",
            f"You are {state.target_GPA - state.current_GPA} points away from your target GPA."]
    )

# initialize user inputs for home page
students_name = input("What is your name? ")
students_GPA = input("What is your current GPA? ")
students_target_GPA = input("What is your target GPA? ")
students_failing = float(students_GPA) < 2.0

# tests
assert_equal(
 index(State(student_name='ryder', current_GPA=3.5, target_GPA=4.0, is_failing=False, courses=[], threshold_test_scores=[])),
 Page(state=State(student_name='ryder',
                 current_GPA=3.5,
                 target_GPA=4.0,
                 is_failing=False,
                 courses=[],
                 threshold_test_scores=[]),
     content=[Header(body='Welcome, ryder.', level=1),
              'Your GPA: 3.5',
              Button(text='Add Course', url='/add_course'),
              Button(text='Remove Course', url='/remove_course'),
              Button(text='View Courses', url='/view_courses'),
              Button(text='Add Test Score', url='/add_test_score'),
              Button(text='View Progress', url='/view_progress')]))

assert_equal(
 add_course(State(student_name='ryder', current_GPA=3.5, target_GPA=4.0, is_failing=False, courses=[], threshold_test_scores=[])),
 Page(state=State(student_name='ryder',
                 current_GPA=3.5,
                 target_GPA=4.0,
                 is_failing=False,
                 courses=[],
                 threshold_test_scores=[]),
     content=['Name of Course:',
              TextBox(name='course_name', kind='text', default_value=''),
              'Number of Credits:',
              TextBox(name='credits', kind='text', default_value='3'),
              'Current Grade:',
              TextBox(name='current_grade', kind='text', default_value='100.0'),
              Button(text='Add Course', url='/append_course'),
              Button(text='Cancel', url='/')]))

assert_equal(
 index(State(student_name='ryder', current_GPA=3.5, target_GPA=4.0, is_failing=False, courses=[], threshold_test_scores=[])),
 Page(state=State(student_name='ryder',
                 current_GPA=3.5,
                 target_GPA=4.0,
                 is_failing=False,
                 courses=[],
                 threshold_test_scores=[]),
     content=[Header(body='Welcome, ryder.', level=1),
              'Your GPA: 3.5',
              Button(text='Add Course', url='/add_course'),
              Button(text='Remove Course', url='/remove_course'),
              Button(text='View Courses', url='/view_courses'),
              Button(text='Add Test Score', url='/add_test_score'),
              Button(text='View Progress', url='/view_progress')]))

start_server(State(students_name, float(students_GPA), float(students_target_GPA), students_failing, [], []))