from dataclasses import dataclass
from bakery import assert_equal
from drafter import *

# set up site metadata
set_site_information(
    author="rydero@udel.edu",
    description="""Student can add/remove courses, record test scores, automatically calculate GPA, 
    and view progress (highest/lowest scores and how far from the target GPA).""",
    sources=["Official Drafter documentation only"],
    planning=["design.jpg"],
    links=["https://github.com/UD-F25-CS1/cs1-website-f25-rydezo/tree/main"]
)
hide_debug_information()
set_website_title("Your Website Title")
set_website_framed(False)

# styling
add_website_css("""
body {
    background-color: #f5f5f5;
    font-family: Arial, sans-serif;
}
h1 {
    background-color: #2c3e50;
    color: white;
    padding: 20px;
    text-align: center;
    border-radius: 10px;
    margin: 10px 0;
}
button {
    background-color: #3498db;
    color: white;
    padding: 10px 20px;
    margin: 5px;
    border-radius: 5px;
    font-weight: bold;
    border: none;
    cursor: pointer;
}
button:hover {
    opacity: 0.8;
}
input, select {
    padding: 8px;
    margin: 5px 0;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 14px;
}
""")

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
    # If no student name set yet, show the web setup form.
    if not state.student_name:
        return setup(state)

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
    update_GPA(state)
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
    if not state.courses:
        return
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

    points_away = round((state.target_GPA - state.current_GPA), 1)
    return Page(
        state,
        content=[f"Your GPA is {state.current_GPA}.",
            f"You are currently {pass_status}",
            f"You are {points_away} points away from your target GPA ({state.target_GPA}).",
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

# Web-based setup for GitHub Pages / static hosting
@route
def setup(state: State) -> Page:
    """
    Setup page to collect student name, current GPA, and target GPA via web form.
    """
    return Page(
        state,
        content=[
            "What's your name?", TextBox(name="students_name", default_value=""),
            "Current GPA:", TextBox(name="students_GPA", default_value="0.0"),
            "Target GPA:", TextBox(name="students_target_GPA", default_value="4.0"),
            Button(text="Start", url="/start_app"),
        ],
    )


@route
def start_app(state: State, students_name: str, students_GPA: str, students_target_GPA: str) -> Page:
    """
    Handler for the setup form. Validates inputs and initializes the app state.
    """
    # validate name (allow spaces in names)
    if not students_name or not students_name.replace(" ", "").isalpha():
        return Page(
            state,
            content=[
                "Please enter a valid name (letters and spaces only).",
                Button("Back", "/setup"),
            ],
        )

    # validate GPAs
    try:
        curr = float(students_GPA)
        targ = float(students_target_GPA)
        if not (0.0 <= curr <= 4.0 and 0.0 <= targ <= 4.0):
            raise ValueError()
    except ValueError:
        return Page(
            state,
            content=[
                "Please enter valid GPAs between 0.0 and 4.0.",
                Button("Back", "/setup"),
            ],
        )

    # initialize state and go to index
    state.student_name = students_name
    state.current_GPA = curr
    state.target_GPA = targ
    state.is_failing = curr < 2.0
    return index(state)

# tests
assert_equal(
    index(
        State(
            student_name='ryder',
            current_GPA=3.5,
            target_GPA=4.0,
            is_failing=False,
            courses=[],
            all_test_scores={},
        ),
    ),
    Page(
        state=State(
            student_name='ryder',
            current_GPA=3.5,
            target_GPA=4.0,
            is_failing=False,
            courses=[],
            all_test_scores={},
        ),
        content=[
            Header(body='Welcome, ryder.', level=1),
            'Your GPA: 3.5',
            Button(text='Add Course', url='/add_course'),
            Button(text='Remove Course', url='/remove_course'),
            Button(text='View Courses', url='/view_courses'),
            Button(text='Add Test Score', url='/add_test_score'),
            Button(text='View Progress', url='/view_progress'),
        ],
    ),
)

assert_equal(
 add_course(State(student_name='ryder', current_GPA=3.5, target_GPA=4.0, is_failing=False, 
                  courses=[], all_test_scores={})),
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
    view_courses(
        State(
            student_name='ryder',
            current_GPA=4.0,
            target_GPA=4.0,
            is_failing=False,
            courses=[
                Course(course_name='cisc108', credits=3, current_grade=100.0, test_scores=[]),
            ],
            all_test_scores={},
        ),
    ),
    Page(
        state=State(
            student_name='ryder',
            current_GPA=4.0,
            target_GPA=4.0,
            is_failing=False,
            courses=[Course(course_name='cisc108', credits=3, current_grade=100.0, test_scores=[])],
            all_test_scores={},
        ),
        content=[
            "Courses: ['cisc108: A']",
            'Credits: [3]',
            'Grades: [100.0]',
            "Test Scores: ['cisc108 scores: []']",
            Button(text='Update a Grade', url='/update_grade'),
            Button(text='Go to Home', url='/'),
        ],
    ),
)

assert_equal(
 update_grade(State(student_name='ryder', current_GPA=4.0, target_GPA=4.0, is_failing=False, 
                    courses=[Course(course_name='cisc108', credits=3, current_grade=100.0, 
                                    test_scores=[])], all_test_scores={})),
 Page(state=State(student_name='ryder',
                 current_GPA=4.0,
                 target_GPA=4.0,
                 is_failing=False,
                 courses=[Course(course_name='cisc108', credits=3, current_grade=100.0, test_scores=[])],
                 all_test_scores={}),
     content=["Which course's grade would you like to update?",
              SelectBox(name='updated_course', options=['cisc108'], default_value=''),
              'What is the new grade?',
              TextBox(name='new_grade', kind='text', default_value=''),
              Button(text='Update Grade', url='/change_grade'),
              Button(text='Cancel', url='/')]))

assert_equal(
 add_test_score(State(student_name='ryder', current_GPA=4.0, target_GPA=4.0, is_failing=False, 
                      courses=[Course(course_name='cisc108', credits=3, current_grade=90.0, 
                                      test_scores=[])], all_test_scores={})),
 Page(state=State(student_name='ryder',
                 current_GPA=4.0,
                 target_GPA=4.0,
                 is_failing=False,
                 courses=[Course(course_name='cisc108', credits=3, current_grade=90.0, test_scores=[])],
                 all_test_scores={}),
     content=['Which course is this test score for?',
              SelectBox(name='course_for_score', options=['cisc108'], default_value=''),
              'What is the test score?',
              TextBox(name='test_score', kind='text', default_value=''),
              Button(text='Add Test Score', url='/append_score'),
              Button(text='Cancel', url='/')]))

assert_equal(
    append_score(
        State(
            student_name='ryder',
            current_GPA=4.0,
            target_GPA=4.0,
            is_failing=False,
            courses=[
                Course(course_name='cisc108', credits=3, current_grade=90.0, test_scores=[]),
            ],
            all_test_scores={},
        ),
        'cisc108',
        '95.0',
    ),
    Page(
        state=State(
            student_name='ryder',
            current_GPA=4.0,
            target_GPA=4.0,
            is_failing=False,
            courses=[Course(course_name='cisc108', credits=3, current_grade=95.0, test_scores=[95.0])],
            all_test_scores={'cisc108': [95.0]},
        ),
        content=[
            Header(body='Welcome, ryder.', level=1),
            'Your GPA: 4.0',
            Button(text='Add Course', url='/add_course'),
            Button(text='Remove Course', url='/remove_course'),
            Button(text='View Courses', url='/view_courses'),
            Button(text='Add Test Score', url='/add_test_score'),
            Button(text='View Progress', url='/view_progress'),
        ],
    ),
)

assert_equal(
    view_progress(
        State(
            student_name='ryder',
            current_GPA=4.0,
            target_GPA=4.0,
            is_failing=False,
            courses=[Course(course_name='cisc108', credits=3, current_grade=95.0, test_scores=[95.0])],
            all_test_scores={'cisc108': [95.0]},
        ),
    ),
    Page(
        state=State(
            student_name='ryder',
            current_GPA=4.0,
            target_GPA=4.0,
            is_failing=False,
            courses=[Course(course_name='cisc108', credits=3, current_grade=95.0, test_scores=[95.0])],
            all_test_scores={'cisc108': [95.0]},
        ),
        content=[
            'Your GPA is 4.0.',
            'You are currently passing. Good job!',
            'You are 0.0 points away from your target GPA (4.0).',
            'Your course with the highest grade: cisc108 (95.0%)',
            'Your course with the lowest grade: cisc108 (95.0%)',
            "Highest test score: ('95.0%', 'cisc108')",
            "Lowest test score: ('95.0%', 'cisc108')",
            Button(text='Go to Home', url='/'),
        ],
    ),
)

assert_equal(
    index(
        State(
            student_name='ryder',
            current_GPA=4.0,
            target_GPA=4.0,
            is_failing=False,
            courses=[
                Course(course_name='cisc108', credits=3, current_grade=95.0, test_scores=[95.0]),
            ],
            all_test_scores={'cisc108': [95.0]},
        ),
    ),
    Page(
        state=State(
            student_name='ryder',
            current_GPA=4.0,
            target_GPA=4.0,
            is_failing=False,
            courses=[Course(course_name='cisc108', credits=3, current_grade=95.0, test_scores=[95.0])],
            all_test_scores={'cisc108': [95.0]},
        ),
        content=[
            Header(body='Welcome, ryder.', level=1),
            'Your GPA: 4.0',
            Button(text='Add Course', url='/add_course'),
            Button(text='Remove Course', url='/remove_course'),
            Button(text='View Courses', url='/view_courses'),
            Button(text='Add Test Score', url='/add_test_score'),
            Button(text='View Progress', url='/view_progress'),
        ],
    ),
)

assert_equal(
    remove_course(
        State(
            student_name='ryder',
            current_GPA=3.5,
            target_GPA=4.0,
            is_failing=False,
            courses=[Course(course_name='cisc108', credits=3, current_grade=100.0, test_scores=[])],
            all_test_scores={},
        )
    ),
    Page(
        state=State(
            student_name='ryder',
            current_GPA=3.5,
            target_GPA=4.0,
            is_failing=False,
            courses=[Course(course_name='cisc108', credits=3, current_grade=100.0, test_scores=[])],
            all_test_scores={},
        ),
        content=[
            'Name of Course:',
            TextBox(name='course_name', kind='text', default_value=''),
            Button(text='Remove Course', url='/delete_course'),
            Button(text='Cancel', url='/index'),
        ],
    ),
)

test_state_invalid_credits = State(
    student_name='alice',
    current_GPA=3.0,
    target_GPA=4.0,
    is_failing=False,
    courses=[],
    all_test_scores={}
)
assert_equal(
    append_course(test_state_invalid_credits, 'math101', 'not_a_number', '85.0'),
    Page(
        state=test_state_invalid_credits,
        content=[
            "Invalid input(s). Please try again.",
            Button("Add Course", "/add_course"),
            Button("Go to Home", "/index"),
        ],
    ),
)

test_state_invalid_grade = State(
    student_name='bob',
    current_GPA=3.0,
    target_GPA=4.0,
    is_failing=False,
    courses=[],
    all_test_scores={}
)
assert_equal(
    append_course(test_state_invalid_grade, 'chem101', '3', 'invalid_grade'),
    Page(
        state=test_state_invalid_grade,
        content=[
            "Invalid input(s). Please try again.",
            Button("Add Course", "/add_course"),
            Button("Go to Home", "/index"),
        ],
    ),
)

test_state_invalid_change = State(
    student_name='carol',
    current_GPA=3.0,
    target_GPA=4.0,
    is_failing=False,
    courses=[Course(course_name='phys101', credits=3, current_grade=85.0, test_scores=[])],
    all_test_scores={},
)
assert_equal(
    change_grade(test_state_invalid_change, 'phys101', 'not_valid'),
    Page(
        state=test_state_invalid_change,
        content=[
            "Invalid grade input. Please try again.",
            Button("Update a Grade", "/update_grade"),
            Button("Go to Home", "/index"),
        ],
    ),
)

assert_equal(
    view_courses(
        State(
            student_name='dan',
            current_GPA=0.0,
            target_GPA=4.0,
            is_failing=True,
            courses=[],
            all_test_scores={},
        )
    ),
    Page(
        state=State(
            student_name='dan',
            current_GPA=0.0,
            target_GPA=4.0,
            is_failing=True,
            courses=[],
            all_test_scores={},
        ),
        content=[
            "You currently have no courses added. Please add some to view them.",
            Button("Add Course", "/add_course"),
            Button("Go to Home", "/index"),
        ],
    ),
)

assert_equal(
    add_test_score(
        State(
            student_name='eve',
            current_GPA=0.0,
            target_GPA=4.0,
            is_failing=True,
            courses=[],
            all_test_scores={},
        )
    ),
    Page(
        state=State(
            student_name='eve',
            current_GPA=0.0,
            target_GPA=4.0,
            is_failing=True,
            courses=[],
            all_test_scores={},
        ),
        content=[
            "You currently have no courses added. Please add some to add test scores.",
            Button("Add Course", "/add_course"),
            Button("Go to Home", "/index"),
        ],
    ),
)

# additional tests to increase coverage

# Test get_letter_grade for all grade ranges
test_course_a = Course(course_name='test_a', credits=3, current_grade=95.0, test_scores=[])
assert_equal(get_letter_grade(test_course_a), 'A')

test_course_b = Course(course_name='test_b', credits=3, current_grade=85.0, test_scores=[])
assert_equal(get_letter_grade(test_course_b), 'B')

test_course_c = Course(course_name='test_c', credits=3, current_grade=75.0, test_scores=[])
assert_equal(get_letter_grade(test_course_c), 'C')

test_course_d = Course(course_name='test_d', credits=3, current_grade=65.0, test_scores=[])
assert_equal(get_letter_grade(test_course_d), 'D')

test_course_f = Course(course_name='test_f', credits=3, current_grade=55.0, test_scores=[])
assert_equal(get_letter_grade(test_course_f), 'F')

# Test view_progress with failing status
test_state_failing = State(
    student_name='failing_student',
    current_GPA=1.5,
    target_GPA=3.0,
    is_failing=True,
    courses=[Course(course_name='hard_class', credits=3, current_grade=65.0, test_scores=[65.0])],
    all_test_scores={'hard_class': [65.0]},
)
assert_equal(
    view_progress(test_state_failing),
    Page(
        state=test_state_failing,
        content=[
            'Your GPA is 1.5.',
            'You are currently failing. You need to lock in!',
            'You are 1.5 points away from your target GPA (3.0).',
            'Your course with the highest grade: hard_class (65.0%)',
            'Your course with the lowest grade: hard_class (65.0%)',
            "Highest test score: ('65.0%', 'hard_class')",
            "Lowest test score: ('65.0%', 'hard_class')",
            Button(text='Go to Home', url='/'),
        ],
    ),
)

# Test update_GPA with all different grade point ranges
test_state_all_grades = State(
    student_name='multi_grade',
    current_GPA=0.0,
    target_GPA=4.0,
    is_failing=True,
    courses=[
        Course(course_name='a_class', credits=3, current_grade=92.0, test_scores=[]),  # 4.0
        Course(course_name='b_class', credits=3, current_grade=85.0, test_scores=[]),  # 3.0
        Course(course_name='c_class', credits=3, current_grade=75.0, test_scores=[]),  # 2.0
        Course(course_name='d_class', credits=3, current_grade=65.0, test_scores=[]),  # 1.0
        Course(course_name='f_class', credits=3, current_grade=50.0, test_scores=[]),  # 0.0
    ],
    all_test_scores={},
)
update_GPA(test_state_all_grades)
assert_equal(test_state_all_grades.current_GPA, 2.0)  # (4.0*3 + 3.0*3 + 2.0*3 + 1.0*3 + 0.0*3) / 15 = 30/15 = 2.0
assert_equal(test_state_all_grades.is_failing, False)

# Test update_GPA when courses list is empty
test_state_no_courses = State(
    student_name='no_courses',
    current_GPA=0.0,
    target_GPA=4.0,
    is_failing=True,
    courses=[],
    all_test_scores={},
)
update_GPA(test_state_no_courses)
assert_equal(test_state_no_courses.current_GPA, 0.0)  # Should remain unchanged

# Test delete_course when course doesn't exist
test_state_delete_nonexistent = State(
    student_name='delete_test',
    current_GPA=3.0,
    target_GPA=4.0,
    is_failing=False,
    courses=[Course(course_name='existing', credits=3, current_grade=85.0, test_scores=[])],
    all_test_scores={},
)
result = delete_course(test_state_delete_nonexistent, 'nonexistent_course')
# Course list should remain unchanged
assert_equal(len(test_state_delete_nonexistent.courses), 1)
assert_equal(test_state_delete_nonexistent.courses[0].course_name, 'existing')

# Test get_highest_score and get_lowest_score with multiple courses
test_state_multi_scores = State(
    student_name='multi_test',
    current_GPA=3.0,
    target_GPA=4.0,
    is_failing=False,
    courses=[
        Course(course_name='course1', credits=3, current_grade=90.0, test_scores=[85.0, 95.0]),
        Course(course_name='course2', credits=3, current_grade=80.0, test_scores=[70.0, 90.0]),
        Course(course_name='course3', credits=3, current_grade=75.0, test_scores=[60.0, 80.0]),
    ],
    all_test_scores={
        'course1': [85.0, 95.0],
        'course2': [70.0, 90.0],
        'course3': [60.0, 80.0],
    },
)
assert_equal(get_highest_score(test_state_multi_scores), ('95.0%', 'course1'))
assert_equal(get_lowest_score(test_state_multi_scores), ('60.0%', 'course3'))

# Test view_progress with multiple courses to verify highest/lowest course detection
test_state_multi_courses = State(
    student_name='multi_courses',
    current_GPA=3.0,
    target_GPA=3.5,
    is_failing=False,
    courses=[
        Course(course_name='high_course', credits=3, current_grade=95.0, test_scores=[95.0]),
        Course(course_name='mid_course', credits=3, current_grade=85.0, test_scores=[85.0]),
        Course(course_name='low_course', credits=3, current_grade=75.0, test_scores=[75.0]),
    ],
    all_test_scores={
        'high_course': [95.0],
        'mid_course': [85.0],
        'low_course': [75.0],
    },
)
assert_equal(
    view_progress(test_state_multi_courses),
    Page(
        state=test_state_multi_courses,
        content=[
            'Your GPA is 3.0.',
            'You are currently passing. Good job!',
            'You are 0.5 points away from your target GPA (3.5).',
            'Your course with the highest grade: high_course (95.0%)',
            'Your course with the lowest grade: low_course (75.0%)',
            "Highest test score: ('95.0%', 'high_course')",
            "Lowest test score: ('75.0%', 'low_course')",
            Button(text='Go to Home', url='/'),
        ],
    ),
)

# Test append_score updates course grade correctly with multiple scores
test_state_multi_test_scores = State(
    student_name='test_scores',
    current_GPA=4.0,
    target_GPA=4.0,
    is_failing=False,
    courses=[Course(course_name='calc', credits=3, current_grade=90.0, test_scores=[90.0])],
    all_test_scores={'calc': [90.0]},
)
append_score(test_state_multi_test_scores, 'calc', '80.0')
# Average should be (90.0 + 80.0) / 2 = 85.0
assert_equal(test_state_multi_test_scores.courses[0].current_grade, 85.0)
assert_equal(test_state_multi_test_scores.courses[0].test_scores, [90.0, 80.0])
assert_equal(test_state_multi_test_scores.all_test_scores['calc'], [90.0, 80.0])

# Test update_GPA sets is_failing correctly when GPA drops below 2.0
test_state_failing_gpa = State(
    student_name='failing_gpa',
    current_GPA=4.0,
    target_GPA=4.0,
    is_failing=False,
    courses=[Course(course_name='fail_course', credits=3, current_grade=55.0, test_scores=[])],
    all_test_scores={},
)
update_GPA(test_state_failing_gpa)
assert_equal(test_state_failing_gpa.current_GPA, 0.0)
assert_equal(test_state_failing_gpa.is_failing, True)

# Test update_GPA at exact boundary (2.0 should not be failing)
test_state_boundary = State(
    student_name='boundary',
    current_GPA=0.0,
    target_GPA=4.0,
    is_failing=True,
    courses=[Course(course_name='c_course', credits=3, current_grade=70.0, test_scores=[])],
    all_test_scores={},
)
update_GPA(test_state_boundary)
assert_equal(test_state_boundary.current_GPA, 2.0)
assert_equal(test_state_boundary.is_failing, False)

# append_course with valid inputs adds a course and updates GPA
test_state = State(
    student_name='alice',
    current_GPA=0.0,
    target_GPA=4.0,
    is_failing=True,
    courses=[],
    all_test_scores={}
)
assert_equal(
    append_course(test_state, 'math101', '3', '85.0'),
    index(
        State(
            student_name='alice',
            current_GPA=3.0,
            target_GPA=4.0,
            is_failing=False,
            courses=[
                Course(
                    course_name='math101',
                    credits=3,
                    current_grade=85.0,
                    test_scores=[],
                )
            ],
            all_test_scores={}
        )
    ),
)

# change_grade with valid input updates the course and GPA
test_state2 = State(
    student_name='bob',
    current_GPA=3.0,
    target_GPA=4.0,
    is_failing=False,
    courses=[Course(course_name='chem101', credits=3, current_grade=80.0, test_scores=[])],
    all_test_scores={},
)
assert_equal(
    change_grade(test_state2, 'chem101', '92'),
    index(
        State(
            student_name='bob',
            current_GPA=4.0,
            target_GPA=4.0,
            is_failing=False,
            courses=[
                Course(
                    course_name='chem101',
                    credits=3,
                    current_grade=92.0,
                    test_scores=[],
                )
            ],
            all_test_scores={},
        )
    ),
)

# append_score with invalid input returns an error page
test_state3 = State(
    student_name='carol',
    current_GPA=0.0,
    target_GPA=4.0,
    is_failing=True,
    courses=[Course(course_name='eng101', credits=3, current_grade=0.0, test_scores=[])],
    all_test_scores={},
)
assert_equal(
    append_score(test_state3, 'eng101', 'not_a_number'),
    Page(
        state=test_state3,
        content=[
            "Invalid test score input. Please try again.",
            Button("Add Test Score", "/add_test_score"),
            Button("Go to Home", "/index"),
        ],
    ),
)

# delete_course removes the named course and updates GPA
test_state4 = State(
    student_name='dan',
    current_GPA=0.0,
    target_GPA=4.0,
    is_failing=True,
    courses=[
        Course(course_name='a', credits=3, current_grade=90.0, test_scores=[]),
        Course(course_name='b', credits=3, current_grade=70.0, test_scores=[]),
    ],
    all_test_scores={},
)
assert_equal(
    delete_course(test_state4, 'a'),
    index(
        State(
            student_name='dan',
            current_GPA=2.0,
            target_GPA=4.0,
            is_failing=False,
            courses=[Course(course_name='b', credits=3, current_grade=70.0, test_scores=[])],
            all_test_scores={},
        )
    ),
)

# get_highest_score / get_lowest_score on empty data
empty_state = State(
    student_name='eve', current_GPA=0.0, target_GPA=4.0, is_failing=True, courses=[], all_test_scores={}
)
assert_equal(get_highest_score(empty_state), (None, None))
assert_equal(get_lowest_score(empty_state), (None, None))

# get_highest_score / get_lowest_score on populated data
pop_state = State(
    student_name='frank',
    current_GPA=0.0,
    target_GPA=4.0,
    is_failing=True,
    courses=[Course(course_name='x', credits=3, current_grade=90.0, test_scores=[88.0, 92.0])],
    all_test_scores={'x': [88.0, 92.0]},
)
assert_equal(get_highest_score(pop_state), ('92.0%', 'x'))
assert_equal(get_lowest_score(pop_state), ('88.0%', 'x'))

# --- new tests: web setup and start_app handler ---
# setup page renders inputs and Start button
test_setup_state = State(student_name='', current_GPA=0.0, target_GPA=4.0, is_failing=True, courses=[], all_test_scores={})
assert_equal(
    setup(test_setup_state),
    Page(
        state=test_setup_state,
        content=[
            "What's your name?",
            TextBox(name='students_name', kind='text', default_value=''),
            'Current GPA:',
            TextBox(name='students_GPA', kind='text', default_value='0.0'),
            'Target GPA:',
            TextBox(name='students_target_GPA', kind='text', default_value='4.0'),
            Button(text='Start', url='/start_app'),
        ],
    ),
)

# start_app with invalid name (numbers) returns error page referencing the same state
test_start_invalid = State(student_name='', current_GPA=0.0, target_GPA=4.0, is_failing=True, courses=[], all_test_scores={})
assert_equal(
    start_app(test_start_invalid, '1234', '3.0', '3.5'),
    Page(
        state=test_start_invalid,
        content=[
            'Please enter a valid name (letters and spaces only).',
            Button('Back', '/setup'),
        ],
    ),
)

# start_app with valid inputs initializes state and returns the index page
test_start_ok = State(student_name='', current_GPA=0.0, target_GPA=4.0, is_failing=True, courses=[], all_test_scores={})
assert_equal(
    start_app(test_start_ok, 'Zoe', '3.2', '3.8'),
    index(
        State(
            student_name='Zoe',
            current_GPA=3.2,
            target_GPA=3.8,
            is_failing=False,
            courses=[],
            all_test_scores={},
        )
    ),
)

start_server(
    State(
        "",
        0.0,
        4.0,
        True,
        [],
        {},
    ),
)