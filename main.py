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

@route
def index(state: State) -> Page:
    """
    Home page showing welcome message, current GPA, and navigation buttons.

    Args:
        state (State): The current state of the application, including student information.
    Returns:
        Page: The home page with welcome message, GPA, and navigation buttons.
    """
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

@route
def add_course(state: State) -> Page:
    """
    Page to add a new course with input fields for course name, credits, and current grade.

    Args:
        state (State): The current state of the application.
    Returns:
        Page: The page with input fields to add a new course.
    """
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

@route
def append_course(state: State, course_name: str, credits: str, current_grade: str) -> Page:
    """
    Appends a new course to the state after validating inputs.

    Args:
        state (State): The current state of the application.
        course_name (str): The name of the course to be added.
        credits (str): The number of credits for the course.
        current_grade (str): The current grade for the course.
    Returns:
        Page: The updated home page after adding the course or an error message if inputs are invalid.
    """
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

@route
def remove_course(state: State) -> Page:
    """
    Page to remove an existing course by specifying its name.

    Args:
        state (State): The current state of the application.
    Returns:
        Page: The page with input field to remove a course.
    """
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
    """
    Deletes a course from the state based on the provided course name.
    
    Args:
        state (State): The current state of the application.
        course_name (str): The name of the course to be removed.
    Returns:
        Page: The updated home page after removing the course.
    """
    for course in state.courses:
        if course.course_name == course_name:
            state.courses.remove(course)
    return index(state)

@route
def view_courses(state: State) -> Page:
    """
    Page to view all added courses along with their details.

    Args:
        state (State): The current state of the application.
    Returns:
        Page: The page displaying all courses with their names, credits, grades, and test scores
    """
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
    """
    Converts a numeric grade to a letter grade.

    Args:
        course (Course): The course object containing the current grade.
    Returns:
        str: The letter grade corresponding to the numeric grade.
    """
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
    """
    Page to update the grade of an existing course.

    Args:
        state (State): The current state of the application.
    Returns:
        Page: The page with input fields to update a course's grade.
    """
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
    """
    Updates the grade of a specified course after validating the input.

    Args:
        state (State): The current state of the application.
        updated_course (str): The name of the course to be updated.
        new_grade (str): The new grade to be set for the course.
    Returns:
        Page: The updated home page after changing the course grade or an error message if input is
    """
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

@route
def add_test_score(state: State) -> Page:
    """
    Page to add a test score for an existing course.

    Args:
        state (State): The current state of the application.
    Returns:
        Page: The page with input fields to add a test score to a course.
    """
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
    """
    Appends a test score to the specified course after validating the input.

    Args:
        state (State): The current state of the application.
        course_for_score (str): The name of the course to which the test score will be added.
        test_score (str): The test score to be added.
    Returns:
        Page: The updated home page after adding the test score or an error message if input is
    """
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
    """
    Updates the current GPA of the student based on their courses and grades.

    Args:
        state (State): The current state of the application.
    Returns:
        None
    """
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

@route
def view_progress(state: State) -> Page:
    """
    Page to view overall progress including GPA, pass/fail status

    Args:
        state (State): The current state of the application.
    Returns:
        Page: The page displaying overall progress details.
    """
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
    """
    Retrieves the highest test score and its corresponding course.

    Args:
        state (State): The current state of the application.
    Returns:
        tuple: A tuple containing the highest test score as a string with '%' and the course name
    """
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
    """
    Retrieves the lowest test score and its corresponding course.
    
    Args:
        state (State): The current state of the application.
    Returns:
        tuple: A tuple containing the lowest test score as a string with '%' and the course name
    """
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