CodeCraftHub

A tiny, beginner-friendly REST API built with Python and Flask to track courses you want to learn. Data is stored in a simple JSON file (no database). This project is great for learning REST API basics, working with JSON data, and experimenting with HTTP methods.
1) Project overview

CodeCraftHub is a minimal learning project that lets developers:

    Create (POST) a course
    Read (GET) one or all courses
    Update (PUT) a course
    Delete (DELETE) a course

Key ideas you’ll learn:

    How to design a REST API for CRUD operations
    How to store data without a database (JSON file)
    How to validate input (required fields, date format, allowed statuses)
    Basic error handling (400, 404, 500 scenarios)

2) Features

    CRUD operations on courses via REST API
    Data persisted to a JSON file named

    courses.json

    Auto-generated integer IDs starting from 1
    Required fields:
        name
        description
        target_date (YYYY-MM-DD)
        status (Not Started, In Progress, or Completed)
    Automatically generated created_at timestamp for each course
    Endpoints accessible under

    /api/courses

    (and

    /api/courses/

    as well)
    Basic error handling for common issues (missing fields, invalid data, not found)

3) Installation instructions (step-by-step)

Prerequisites:

    Python 3.x (recommended 3.8+)
    Internet access to install packages (if needed)

Step-by-step:

    Create a project folder

    Example: mkdir CodeCraftHub
    Navigate into it: cd CodeCraftHub

    Create a Python virtual environment (optional but recommended)

    macOS/Linux:
        python3 -m venv venv
        source venv/bin/activate
    Windows:
        python -m venv venv
        .\venv\Scripts\activate

    Install Flask

    pip install Flask

    Save the application code

    Create a file named app.py and paste the complete Flask app (the CodeCraftHub API) into it.
    Also ensure there is no pre-existing

    courses.json

    in the folder; the app will create it automatically when you run.

    Run the application

    python app.py
    The server runs on http://127.0.0.1:5000 by default

    Verify the JSON data store

    The app will create a

    data/courses.json

    or just

    courses.json

    (depending on your version) automatically when you first create a course.

Notes:

    The app is designed to be beginner-friendly and self-contained.
    You can stop the server with Ctrl+C.

4) How to run the application

    Start the Flask app:
        python app.py
    Visit (manual checks):
        http://127.0.0.1:5000/api/courses
        http://127.0.0.1:5000/api/courses?id=1

The API accepts both with and without a trailing slash for the routes, thanks to Flask route definitions.
5) API endpoints documentation (with examples)

Base path: /api/courses

    POST /api/courses (Create a new course)
        Body (JSON): { "name": "Intro to Python", "description": "Learn Python basics", "target_date": "YYYY-MM-DD", "status": "Not Started" }
        Success response:
            Status: 201 Created
            Body: the created course object, including id and created_at
            Example: { "id": 1, "name": "Intro to Python", "description": "Learn Python basics", "target_date": "2026-12-31", "status": "Not Started", "created_at": "2026-04-23T12:34:56Z" }

    GET /api/courses (Get all courses)
        Success response:
        Status: 200 OK
        Body: a JSON array of course objects
        Example: [ { "id": 1, "name": "Intro to Python", "description": "Learn Python basics", "target_date": "2026-12-31", "status": "Not Started", "created_at": "2026-04-23T12:34:56Z" } ]

    GET /api/courses?id=<ID> (Get a specific course by id)
        Example: GET /api/courses?id=1
        Success response:
            Status: 200 OK
            Body: a single course object (not wrapped in an array)

    PUT /api/courses (Update a course)
        Body (JSON) - full update (must include id) { "id": 1, "name": "Intro to Python - Updated", "description": "Updated description", "target_date": "2027-01-15", "status": "In Progress" }
        Success response:
            Status: 200 OK
            Body: the updated course object
            Example: { "id": 1, "name": "Intro to Python - Updated", "description": "Updated description", "target_date": "2027-01-15", "status": "In Progress", "created_at": "2026-04-23T12:34:56Z" }

    DELETE /api/courses (Delete a course)
        Body (JSON) - must include id { "id": 1 }
        Success response:
            Status: 200 OK
            Body: the deleted course object
            Example: { "id": 1, "name": "Intro to Python", "description": "Learn Python basics", "target_date": "2026-12-31", "status": "Not Started", "created_at": "2026-04-23T12:34:56Z" }

Notes:

    The API also supports a trailing slash variant for each route (e.g., /api/courses/). Both forms are accepted.

6) Testing instructions

Manual testing (curl is easiest to start):

    Create a course
        curl -X POST -H "Content-Type: application/json" -d '{ "name": "Intro to Python", "description": "Learn Python basics", "target_date": "2026-12-31", "status": "Not Started" }' http://127.0.0.1:5000/api/courses

    Get all courses
        curl http://127.0.0.1:5000/api/courses

    Get a course by id
        curl "http://127.0.0.1:5000/api/courses?id=1"

    Update a course
        curl -X PUT -H "Content-Type: application/json" -d '{ "id": 1, "name": "Intro to Python - Updated", "description": "Updated details", "target_date": "2027-01-15", "status": "In Progress" }' http://127.0.0.1:5000/api/courses

    Delete a course
        curl -X DELETE -H "Content-Type: application/json" -d '{"id": 1}' http://127.0.0.1:5000/api/courses

Automated tests (optional):

    You can use a Python unittest script (or pytest) to automate checks. A simple example test script (already provided in the repository) will:
        Create a course (POST)
        Retrieve all courses (GET)
        Retrieve a specific course (GET with id)
        Update a course (PUT)
        Delete a course (DELETE)
        Validate error scenarios (missing fields, invalid data, not found)

Run example:

    python app.py # start the server
    python tests_codecrafthub_api.py # run automated tests (if you saved the test file)

7) Troubleshooting common issues

    Server won’t start or port already in use
        Ensure no other process is using port 5000.
        Change the port in app.py if needed (not required for this simple setup).

    ModuleNotFoundError: No module named 'flask'
        Activate your virtual environment and install Flask:
            pip install Flask

    JSON decode errors or corrupted data file
        The app handles corrupted data gracefully by treating it as an empty list.
        If you see odd behavior, you can remove or reset the data file:
            Delete courses.json (or data/courses.json depending on your setup) and restart the server.

    Permission issues when writing data
        Ensure the directory where

        courses.json

        is stored is writable.
        On systems with strict permissions, run the app with appropriate permissions, or set write permissions for the file.

    Invalid input errors (date format, status)
        The API expects:
            target_date in YYYY-MM-DD format (e.g., 2026-12-31)
            status one of: Not Started, In Progress, Completed
        Double-check your payloads for correct field names and values.

    GET by non-existent ID returns 404
        Use an ID you know exists, or test with a large ID like 999999 to verify 404 behavior.

8) Project structure explanation

A simple, beginner-friendly layout (single-file approach)

CodeCraftHub/

    app.py # The Flask app implementing the REST API
    courses.json # Data store (created automatically, if missing)
    (optional) tests_codecrafthub_api.py # Automated tests (uncomment and run)

Files explanation:

    app.py
        Contains the Flask app, route definitions for POST, GET, PUT, DELETE under /api/courses
        Validates input, auto-generates IDs, and writes to/reads from the JSON file
        Creates created_at timestamp when a course is created
        Handles common errors and returns appropriate HTTP status codes

    courses.json
        A flat JSON array that stores course objects
        Each course has: id, name, description, target_date, status, created_at

    tests_codecrafthub_api.py (optional)
        A self-contained Python script to automate testing of the API
        Includes curl command snippets and payload examples for convenience