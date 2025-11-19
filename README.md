### Purpose
Students input their test scores across multiple subjects. The app analyzes trends, identifies strengths and weaknesses, and offers personalized study suggestions.

### Features
- Add and remove courses with credits and current grade.
- Record test scores per course and auto-update course grades.
- View current GPA, progress toward a target GPA, and identify highest/lowest courses and test scores.
- Lightweight web UI served by the `drafter` framework with simple forms and navigation.

### Installation
Requires Python 3.10+.

1. Create and activate a virtual environment (PowerShell):

```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies (the project relies on `drafter` and `bakery` used in tests):

```
pip install drafter bakery
```

If the exact package names differ in your environment, install the packages that provide the `drafter` UI primitives and `bakery.assert_equal` used by the tests.

### Usage
Run the app from the project root:

```
python main.py
```

The script will prompt for a student name, current GPA, and target GPA and then start the Drafter server. Open the URL printed by the server in your browser to interact with the UI.

There are also lightweight bakery asserts in `main.py` that exercise the page-building functions; these run on startup before the server launches.

### Styling
This project applies general styling to the Drafter pages. Styling is implemented directly in `main.py` (CSS injected via the Drafter helper). For guidelines and additional style classes provided by Drafter, see the Drafter styling docs:

https://drafter-edu.github.io/drafter/students/styling.html

You can customize colors, spacing, and controls by editing the CSS block (or by creating a dedicated stylesheet and loading it via Drafter helpers).

### Development
- After making changes, run `python main.py` to verify pages render and tests pass.
- When changing page structure, update the bakery asserts in `main.py` or convert them into dedicated unit tests.