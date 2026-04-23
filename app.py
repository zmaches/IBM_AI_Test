import json
import os
from datetime import datetime
from flask import Flask, request, jsonify

# ----------------------------
# Configuration and helpers
# ----------------------------

# Data file name (in project root)
DATA_FILE = 'courses.json'

# Allowed statuses for a course
ALLOWED_STATUSES = {"Not Started", "In Progress", "Completed"}

# Ensure the data file exists; if not, create with an empty list
def ensure_data_file():
    if not os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2)
        except Exception as e:
            # If we fail here, there's no point continuing; print for debugging
            print(f"Error creating data file {DATA_FILE}: {e}")

# Load courses from the JSON file
def load_courses():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # If the file somehow disappears, recreate it and return empty list
        ensure_data_file()
        return []
    except json.JSONDecodeError:
        # If the JSON is corrupted, reset to an empty list
        return []
    except Exception as e:
        # Re-raise for the caller to handle as a 500 error
        raise e

# Save the list of courses back to the JSON file
def save_courses(courses):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(courses, f, indent=2)
        return True
    except Exception as e:
        # Re-raise so the caller can respond with a 500 error
        raise e

# Generate the next auto-incrementing id (starting at 1)
def get_next_id(courses):
    if not courses:
        return 1
    return max(course['id'] for course in courses) + 1

# Validate that target_date has the format YYYY-MM-DD
def is_valid_target_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except (TypeError, ValueError):
        return False

# Create the Flask app
app = Flask(__name__)

# Ensure the data file exists when the app starts
ensure_data_file()

# ----------------------------
# Routes (CRUD)
# ----------------------------

# 1) Create a new course
# POST /api/courses
@app.route('/api/courses', methods=['POST'])
def create_course():
    try:
        data = request.get_json(force=True) or {}
    except Exception:
        return jsonify({"error": "Invalid JSON payload"}), 400

    # Required fields
    required_fields = ['name', 'description', 'target_date', 'status']

    missing_fields = [f for f in required_fields if not data.get(f)]
    if missing_fields:
        return jsonify({
            "error": "Missing required fields",
            "missing_fields": missing_fields
        }), 400

    # Validate target_date format
    if not is_valid_target_date(data['target_date']):
        return jsonify({
            "error": "Invalid target_date format. Expected YYYY-MM-DD."
        }), 400

    # Validate status value
    status = data['status']
    if status not in ALLOWED_STATUSES:
        return jsonify({
            "error": "Invalid status value",
            "allowed": list(ALLOWED_STATUSES)
        }), 400

    try:
        courses = load_courses()
        new_id = get_next_id(courses)
        created_at = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

        course = {
            "id": new_id,
            "name": data['name'],
            "description": data['description'],
            "target_date": data['target_date'],  # expected format: YYYY-MM-DD
            "status": status,
            "created_at": created_at
        }

        courses.append(course)
        save_courses(courses)

        return jsonify(course), 201
    except Exception as e:
        # File I/O or other unexpected errors
        return jsonify({"error": "Failed to create course", "detail": str(e)}), 500

# 2) Get all courses
# GET /api/courses
@app.route('/api/courses', methods=['GET'])
def get_all_courses():
    try:
        courses = load_courses()
        return jsonify(courses), 200
    except Exception as e:
        return jsonify({"error": "Failed to read courses", "detail": str(e)}), 500

# 3) Get a specific course by id
# GET /api/courses/<int:course_id>
@app.route('/api/courses/<int:course_id>', methods=['GET'])
def get_course(course_id):
    try:
        courses = load_courses()
        course = next((c for c in courses if c['id'] == course_id), None)
        if course is None:
            return jsonify({"error": "Course not found"}), 404
        return jsonify(course), 200
    except Exception as e:
        return jsonify({"error": "Failed to read course", "detail": str(e)}), 500

# 4) Update a course
# PUT /api/courses/<int:course_id>
# For PUT, we replace allowed fields. All fields (name, description, target_date, status)
# are required in the update payload to keep behavior explicit.
@app.route('/api/courses/<int:course_id>', methods=['PUT'])
def update_course(course_id):
    try:
        data = request.get_json(force=True) or {}
    except Exception:
        return jsonify({"error": "Invalid JSON payload"}), 400

    # Required fields for a full update
    required_fields = ['name', 'description', 'target_date', 'status']
    missing_fields = [f for f in required_fields if f not in data or not data.get(f)]
    if missing_fields:
        return jsonify({
            "error": "Missing required fields for update",
            "missing_fields": missing_fields
        }), 400

    # Validate target_date format
    if not is_valid_target_date(data['target_date']):
        return jsonify({"error": "Invalid target_date format. Expected YYYY-MM-DD."}), 400

    # Validate status value
    status = data['status']
    if status not in ALLOWED_STATUSES:
        return jsonify({
            "error": "Invalid status value",
            "allowed": list(ALLOWED_STATUSES)
        }), 400

    try:
        courses = load_courses()
        course = next((c for c in courses if c['id'] == course_id), None)
        if course is None:
            return jsonify({"error": "Course not found"}), 404

        # Preserve created_at; update fields
        course['name'] = data['name']
        course['description'] = data['description']
        course['target_date'] = data['target_date']
        course['status'] = status

        save_courses(courses)
        return jsonify(course), 200
    except Exception as e:
        return jsonify({"error": "Failed to update course", "detail": str(e)}), 500

# 5) Delete a course
# DELETE /api/courses/<int:course_id>
@app.route('/api/courses/<int:course_id>', methods=['DELETE'])
def delete_course(course_id):
    try:
        courses = load_courses()
        index = next((i for i, c in enumerate(courses) if c['id'] == course_id), None)
        if index is None:
            return jsonify({"error": "Course not found"}), 404

        removed_course = courses.pop(index)
        save_courses(courses)
        return jsonify({"message": "Course deleted", "course": removed_course}), 200
    except Exception as e:
        return jsonify({"error": "Failed to delete course", "detail": str(e)}), 500

# ----------------------------
# Run the app
# ----------------------------
if __name__ == '__main__':
    # Ensure the data file exists before starting the server
    ensure_data_file()
    # Run the Flask development server
    app.run(debug=True)