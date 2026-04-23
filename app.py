from flask import Flask, request, jsonify
from datetime import datetime
import json
import os

# -----------------------------
# Configuration and helpers
# -----------------------------

DATA_FILE = 'courses.json'
ALLOWED_STATUSES = {"Not Started", "In Progress", "Completed"}

# Ensure the data file exists (creates an empty list if missing)
def ensure_data_file():
    if not os.path.exists(DATA_FILE):
        dirpath = os.path.dirname(DATA_FILE)
        if dirpath and not os.path.exists(dirpath):
            os.makedirs(dirpath, exist_ok=True)
        with open(DATA_FILE, 'w') as f:
            json.dump([], f, indent=2)

# Load courses from the JSON file
def load_courses():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            else:
                # If the file exists but doesn't contain a list, treat as empty
                return []
    except json.JSONDecodeError:
        # If the JSON is corrupted, treat as empty (optional: you could raise)
        return []
    except Exception as e:
        # For unexpected IO errors, re-raise to be handled by caller
        raise

# Save the entire list of courses back to the JSON file
def save_courses(courses):
    try:
        dirpath = os.path.dirname(DATA_FILE)
        if dirpath and not os.path.exists(dirpath):
            os.makedirs(dirpath, exist_ok=True)
        with open(DATA_FILE, 'w') as f:
            json.dump(courses, f, indent=2)
    except Exception as e:
        # Re-raise so caller can convert to HTTP 500
        raise

# Compute the next incremental id
def next_id(courses):
    if not courses:
        return 1
    max_id = max((c.get('id', 0) for c in courses), default=0)
    return max_id + 1

# Validate payload for required fields and formats
def validate_payload(payload, require_all=True):
    if not isinstance(payload, dict):
        return False, "Invalid payload: expected a JSON object"

    if require_all:
        required = ['name', 'description', 'target_date', 'status']
        for key in required:
            if key not in payload:
                return False, f"Missing required field: {key}"

    if 'target_date' in payload:
        try:
            datetime.strptime(payload['target_date'], "%Y-%m-%d")
        except ValueError:
            return False, "target_date must be in YYYY-MM-DD format"

    if 'status' in payload:
        if payload['status'] not in ALLOWED_STATUSES:
            return False, f"Invalid status. Allowed values: {', '.join(ALLOWED_STATUSES)}"

    return True, ""

# -----------------------------
# Flask app and routes
# -----------------------------
ensure_data_file()  # Create the data file if it doesn't exist

app = Flask(__name__)

# Helper to return a consistent 500 on unexpected IO errors
def handle_io_error(e):
    # In production, log the error here
    return jsonify({'error': 'Internal server error (IO)'}), 500

# POST /api/courses (also accepts /api/courses/)
@app.route('/api/courses', methods=['POST'])
@app.route('/api/courses/', methods=['POST'])
def add_course():
    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({'error': 'Request body must be JSON'}), 400

    ok, msg = validate_payload(payload, require_all=True)
    if not ok:
        return jsonify({'error': msg}), 400

    try:
        courses = load_courses()
    except Exception as e:
        return handle_io_error(e)

    new_id = next_id(courses)
    created_at = datetime.utcnow().isoformat() + 'Z'

    course = {
        'id': new_id,
        'name': payload['name'],
        'description': payload['description'],
        'target_date': payload['target_date'],
        'status': payload['status'],
        'created_at': created_at
    }

    courses.append(course)

    try:
        save_courses(courses)
    except Exception as e:
        return handle_io_error(e)

    return jsonify(course), 201

# GET /api/courses (also accepts /api/courses/)
# - If ?id=X is provided, return a specific course
# - If no id, return all courses
@app.route('/api/courses', methods=['GET'])
@app.route('/api/courses/', methods=['GET'])
def get_courses():
    try:
        courses = load_courses()
    except Exception as e:
        return jsonify({'error': 'Unable to read data file'}), 500

    # If the client asked for a specific course by id
    cid = request.args.get('id')
    if cid is not None:
        try:
            cid_int = int(cid)
        except ValueError:
            return jsonify({'error': 'Invalid id'}), 400

        course = next((c for c in courses if c.get('id') == cid_int), None)
        if course is None:
            return jsonify({'error': 'Course not found'}), 404
        return jsonify(course)

    # No id provided; return all courses
    return jsonify(courses)

# PUT /api/courses (also /api/courses/)
# Full update of a course; requires id and all fields
@app.route('/api/courses', methods=['PUT'])
@app.route('/api/courses/', methods=['PUT'])
def update_course():
    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({'error': 'Request body must be JSON'}), 400

    if 'id' not in payload:
        return jsonify({'error': 'Missing field: id'}), 400

    ok, msg = validate_payload(payload, require_all=True)
    if not ok:
        return jsonify({'error': msg}), 400

    try:
        courses = load_courses()
    except Exception as e:
        return jsonify({'error': 'Unable to read data file'}), 500

    cid = payload['id']
    for idx, c in enumerate(courses):
        if c.get('id') == cid:
            # Preserve created_at; if it somehow wasn't present, create one
            created_at = c.get('created_at', datetime.utcnow().isoformat() + 'Z')
            updated = {
                'id': cid,
                'name': payload['name'],
                'description': payload['description'],
                'target_date': payload['target_date'],
                'status': payload['status'],
                'created_at': created_at
            }
            courses[idx] = updated

            try:
                save_courses(courses)
            except Exception as e:
                return handle_io_error(e)

            return jsonify(updated)

    return jsonify({'error': 'Course not found'}), 404

# DELETE /api/courses (also /api/courses/)
# Delete a course by id (id can be in JSON body or query param ?id=)
@app.route('/api/courses', methods=['DELETE'])
@app.route('/api/courses/', methods=['DELETE'])
def delete_course():
    payload = request.get_json(silent=True)
    cid = None

    # Try to get id from JSON body
    if isinstance(payload, dict) and 'id' in payload:
        cid = payload['id']

    # If not in body, try query parameter
    if cid is None:
        qid = request.args.get('id')
        if qid is not None:
            try:
                cid = int(qid)
            except ValueError:
                return jsonify({'error': 'Invalid id'}), 400

    if cid is None:
        return jsonify({'error': 'Missing field: id'}), 400

    try:
        courses = load_courses()
    except Exception as e:
        return jsonify({'error': 'Unable to read data file'}), 500

    for i, c in enumerate(courses):
        if c.get('id') == cid:
            removed = courses.pop(i)
            try:
                save_courses(courses)
            except Exception as e:
                return handle_io_error(e)
            return jsonify(removed)

    return jsonify({'error': 'Course not found'}), 404

# -----------------------------
# Run the app
# -----------------------------
if __name__ == '__main__':
    # Running in debug mode is convenient for beginners, but disable in production
    app.run(debug=True)