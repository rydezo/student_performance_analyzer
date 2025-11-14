from dataclasses import dataclass
from bakery import assert_equal
from drafter import *

@dataclass
class Course:
    course_name: str
    credits: int
    current_grade: float
    test_scores: list[float]

@dataclass
class State:
    student_name: str
    current_GPA: float
    target_GPA: float
    is_failing: bool
    courses: list[Course]
    all_test_scores: dict[str, list[float]]

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
def append_course(state: State, course_name: str, credits: str, current_grade: str) -> Page:
    # check for valid inputs
    try:
        course_credits = int(credits)
        course_grade = float(current_grade)
    except:
        return Page(
            state,
            content=["Invalid input(s). Please try again.",
             Button("Add Course", "/add_course"),
             Button("Go to Home", "/index")]
        )
    new_course = Course(course_name, course_credits, course_grade, [])
    state.courses.append(new_course)
    update_GPA(state)
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
    
    course_names: list[str] = []
    course_credits: list[int] = []
    course_grades: list[float] = []
    course_test_scores: list[list[float]] = []

    for course in state.courses:
        course_names.append(f"{course.course_name}: {get_letter_grade(course)}")
        course_credits.append(course.credits)
        course_grades.append(course.current_grade)
        course_test_scores.append(f"{course.course_name} scores: {course.test_scores}")
            
    return Page(
        state,
        content=[f"Courses: {course_names}",
                f"Credits: {course_credits}",
                f"Grades: {course_grades}",
                f"Test Scores: {course_test_scores}",
                Button("Update a Grade", "/update_grade"),
                Button("Go to Home", "/index")]
        )

def get_letter_grade(course: Course) -> str:
    letter_grades = {
        "A": range(90,101),
        "B": range(80,90),
        "C": range(70,80),
        "D": range(60,70),
        "F": range(0,60)
    }
    for letter, r in letter_grades.items():
        if int(course.current_grade) in r:
            return letter

@route
def update_grade(state: State) -> Page:
    courses_names: list[str] = [course.course_name for course in state.courses]
    return Page(
        state,
        content=[
            "Which course's grade would you like to update?", SelectBox(name="updated_course", options=courses_names),
            "What is the new grade?", TextBox(name="new_grade"),
            Button(text="Update Grade", url="/change_grade"),
            Button(text="Cancel", url="/index")
        ]
    )

@route
def change_grade(state: State, updated_course: str, new_grade: str):
    # check valid input
    try:
        float_grade = float(new_grade)
    except:
        return Page(
            state,
            content=["Invalid grade input. Please try again.",
             Button("Update a Grade", "/update_grade"),
             Button("Go to Home", "/index")]
        )
    for course in state.courses:
        if course.course_name == updated_course:
            course.current_grade = float_grade
            update_GPA(state)
    return index(state)

# page 5
@route
def add_test_score(state: State) -> Page:
    if not state.courses:
        return Page(
            state,
            content=["You currently have no courses added. Please add some to add test scores.",
             Button("Add Course", "/add_course"),
             Button("Go to Home", "/index")]
        )
    courses_names: list[str] = [course.course_name for course in state.courses]
    return Page(
        state,
        content=[
            "Which course is this test score for?", SelectBox(name="course_for_score", options=courses_names),
            "What is the test score?", TextBox(name="test_score"),
            Button(text="Add Test Score", url="/append_score"),
            Button(text="Cancel", url="/index")
        ]
    )

@route
def append_score(state: State, course_for_score: str, test_score: str):
    # check valid input
    try:
        float_score = float(test_score)
    except:
        return Page(
            state,
            content=["Invalid test score input. Please try again.",
             Button("Add Test Score", "/add_test_score"),
             Button("Go to Home", "/index")]
        )
    
    for course in state.courses:
        if course.course_name == course_for_score:
            course.test_scores.append(float_score)
            if course.course_name not in state.all_test_scores:
                state.all_test_scores[course.course_name] = [float_score]
            else:
                state.all_test_scores[course.course_name].append(float_score)
            # update course grade and GPA
            course.current_grade = round(sum(course.test_scores)/len(course.test_scores), 2)
            update_GPA(state)
    
    return index(state)

def update_GPA(state: State):
    total_grade_points = 0
    total_credits = 0
    for course in state.courses:
        if course.current_grade >= 90:
            course_grade_points = 4.0
        elif course.current_grade >= 80:
            course_grade_points = 3.0
        elif course.current_grade >= 70:
            course_grade_points = 2.0
        elif course.current_grade >= 60:
            course_grade_points = 1.0
        else:
            course_grade_points = 0.0
        total_grade_points += course_grade_points*course.credits
        total_credits += course.credits
    
    state.current_GPA = round(total_grade_points/total_credits, 2)
    state.is_failing = state.current_GPA < 2.0


# page 6
@route
def view_progress(state: State) -> Page:
    if state.is_failing:
        pass_status = "failing. You need to lock in!"
    else:
        pass_status = "passing. Good job!"

    # highest course grade
    high_course = Course("N/A", None, None, None) if not state.courses else state.courses[0]
    for course in state.courses:
        if course.current_grade > high_course.current_grade:
            high_course = course

    # lowest course grade
    low_course = Course("N/A", None, None, None) if not state.courses else state.courses[0]
    for course in state.courses:
        if course.current_grade < low_course.current_grade:
            low_course = course

    return Page(
        state,
        content=[f"Your GPA is {state.current_GPA}.",
            f"You are currently {pass_status}",
            f"You are {round((state.target_GPA - state.current_GPA), 1)} points away from your target GPA ({state.target_GPA}).",
            f"Your course with the highest grade: {high_course.course_name} ({high_course.current_grade}%)",
            f"Your course with the lowest grade: {low_course.course_name} ({low_course.current_grade}%)",
            f"Highest test score: {get_highest_score(state)}",
            f"Lowest test score: {get_lowest_score(state)}",
            Button("Go to Home", "/index")]
    )

def get_highest_score(state: State) -> tuple:
    if not state.all_test_scores:
        return (None, None)
    highest_score = 0
    course_of_highest = "N/A" if not state.courses else state.courses[0].course_name
    for course_name, test_scores in state.all_test_scores.items():
        for test_score in test_scores:
            if test_score > highest_score:
                highest_score = test_score
                course_of_highest = course_name
    return (f'{highest_score}%', course_of_highest)

def get_lowest_score(state: State) -> tuple:
    if not state.all_test_scores:
        return (None, None)
    lowest_score = 100
    course_of_lowest = "N/A" if not state.courses else state.courses[0].course_name
    for course_name, test_scores in state.all_test_scores.items():
        for test_score in test_scores:
            if test_score < lowest_score:
                lowest_score = test_score
                course_of_lowest = course_name
    return (f'{lowest_score}%', course_of_lowest)

# initialize user inputs for home page
students_name = input("What is your name? ")
students_GPA = input("What is your current GPA? ")
students_target_GPA = input("What is your target GPA? ")
students_failing = float(students_GPA) < 2.0

# tests
assert_equal(
 index(State(student_name='ryder', current_GPA=3.5, target_GPA=4.0, is_failing=False, courses=[], all_test_scores={})),
 Page(state=State(student_name='ryder',
                 current_GPA=3.5,
                 target_GPA=4.0,
                 is_failing=False,
                 courses=[],
                 all_test_scores={}),
     content=[Header(body='Welcome, ryder.', level=1),
              'Your GPA: 3.5',
              Button(text='Add Course', url='/add_course'),
              Button(text='Remove Course', url='/remove_course'),
              Button(text='View Courses', url='/view_courses'),
              Button(text='Add Test Score', url='/add_test_score'),
              Button(text='View Progress', url='/view_progress')]))

assert_equal(
 add_course(State(student_name='ryder', current_GPA=3.5, target_GPA=4.0, is_failing=False, courses=[], all_test_scores={})),
 Page(state=State(student_name='ryder',
                 current_GPA=3.5,
                 target_GPA=4.0,
                 is_failing=False,
                 courses=[],
                 all_test_scores={}),
     content=['Name of Course:',
              TextBox(name='course_name', kind='text', default_value=''),
              'Number of Credits:',
              TextBox(name='credits', kind='text', default_value='3'),
              'Current Grade:',
              TextBox(name='current_grade', kind='text', default_value='100.0'),
              Button(text='Add Course', url='/append_course'),
              Button(text='Cancel', url='/')]))

assert_equal(
 index(State(student_name='ryder', current_GPA=3.5, target_GPA=4.0, is_failing=False, courses=[], all_test_scores={})),
 Page(state=State(student_name='ryder',
                 current_GPA=3.5,
                 target_GPA=4.0,
                 is_failing=False,
                 courses=[],
                 all_test_scores={}),
     content=[Header(body='Welcome, ryder.', level=1),
              'Your GPA: 3.5',
              Button(text='Add Course', url='/add_course'),
              Button(text='Remove Course', url='/remove_course'),
              Button(text='View Courses', url='/view_courses'),
              Button(text='Add Test Score', url='/add_test_score'),
              Button(text='View Progress', url='/view_progress')]))

start_server(State(students_name, float(students_GPA), float(students_target_GPA), students_failing, [], {}))