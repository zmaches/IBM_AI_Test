import json
import os
import time
import requests

# Base URL for the running Flask app
BASE_URL = "http://127.0.0.1:5000"
API_COURSES = "/api/courses"

# 1) Curl commands to test each endpoint (easy copy-paste for manual testing)
CURL_SNIPPETS = """
Curl tests (copy-paste; replace placeholders as needed):

POST /api/courses
curl -X POST -H "Content-Type: application/json" -d '{
  "name": "Intro to Python",
  "description": "Learn Python basics",
  "target_date": "2026-12-31",
  "status": "Not Started"
}' http://127.0.0.1:5000/api/courses

GET /api/courses
curl http://127.0.0.1:5000/api/courses

GET /api/courses?id=1
curl "http://127.0.0.1:5000/api/courses?id=1"

PUT /api/courses
curl -X PUT -H "Content-Type: application/json" -d '{
  "id": 1,
  "name": "Intro to Python - Updated",
  "description": "Updated details",
  "target_date": "2027-01-15",
  "status": "In Progress"
}' http://127.0.0.1:5000/api/courses

DELETE /api/courses
curl -X DELETE -H "Content-Type: application/json" -d '{"id": 1}' http://127.0.0.1:5000/api/courses
"""

# 2) Example JSON payloads for POST and PUT requests
POST_PAYLOAD = {
    "name": "Intro to Python",
    "description": "Learn Python basics",
    "target_date": "2026-12-31",
    "status": "Not Started"
}

# PUT payload will be constructed with a real id after creation
PUT_PAYLOAD_TEMPLATE = {
    "id": 1,
    "name": "Intro to Python - Updated",
    "description": "Learn Python basics with updates",
    "target_date": "2027-01-15",
    "status": "In Progress"
}

# Helper: reset the data store to an empty list for repeatable tests
def reset_store():
    if os.path.exists("courses.json"):
        try:
            os.remove("courses.json")
        except Exception as e:
            print("Warning: could not remove courses.json:", e)
    # Create an empty store
    with open("courses.json", "w") as f:
        json.dump([], f, indent=2)
    print("Store reset: courses.json created with []")

# Helpers for API operations
def post_course(payload):
    return requests.post(BASE_URL + API_COURSES, json=payload)

def get_all_courses():
    return requests.get(BASE_URL + API_COURSES)

def get_course_by_id(course_id):
    return requests.get(BASE_URL + API_COURSES, params={"id": course_id})

def put_course(payload):
    return requests.put(BASE_URL + API_COURSES, json=payload)

def delete_course_by_body(payload):
    return requests.delete(BASE_URL + API_COURSES, json=payload)

def delete_course_by_id(course_id):
    return requests.delete(BASE_URL + API_COURSES, json={"id": course_id})

# 3) Comprehensive test runner with both success and error scenarios
def run_tests():
    client = None  # not used, but left for clarity
    print("Starting CodeCraftHub API tests...")

    # Optional: print curl commands to help manual testing
    print("\nCURL test commands (copy-paste):")
    print(CURL_SNIPPETS)

    # 1) Reset store for a clean test environment
    reset_store()
    time.sleep(0.2)

    # 2) POST /api/courses - create a new course
    resp = post_course(POST_PAYLOAD)
    assert resp.status_code == 201, f"POST failed with {resp.status_code}: {resp.text}"
    created = resp.json()
    course_id = created.get("id")
    assert isinstance(course_id, int) and course_id > 0, "POST did not return a valid id"
    print("POST success:", json.dumps(created, indent=2))

    # 3) GET /api/courses - get all courses
    resp = get_all_courses()
    assert resp.status_code == 200, f"GET all failed: {resp.status_code} {resp.text}"
    all_courses = resp.json()
    assert isinstance(all_courses, list), "GET all did not return a list"
    print("GET all count:", len(all_courses))

    # 4) GET /api/courses?id=<id> - get specific course
    resp = get_course_by_id(course_id)
    assert resp.status_code == 200, f"GET by id failed: {resp.status_code} {resp.text}"
    course = resp.json()
    assert course.get("id") == course_id
    print("GET by id:", json.dumps(course, indent=2))

    # 5) PUT /api/courses - update the course
    PUT_PAYLOAD = {
        "id": course_id,
        "name": "Intro to Python - Updated",
        "description": "Learn Python basics with updates",
        "target_date": "2027-01-15",
        "status": "In Progress"
    }
    resp = put_course(PUT_PAYLOAD)
    assert resp.status_code == 200, f"PUT failed: {resp.status_code} {resp.text}"
    updated = resp.json()
    assert updated["id"] == course_id
    assert updated["name"] == PUT_PAYLOAD["name"]
    assert updated["status"] == PUT_PAYLOAD["status"]
    print("PUT success:", json.dumps(updated, indent=2))

    # 6) DELETE /api/courses - delete by id
    resp = delete_course_by_id(course_id)
    assert resp.status_code == 200, f"DELETE failed: {resp.status_code} {resp.text}"
    deleted = resp.json()
    assert deleted.get("id") == course_id
    print("DELETE success:", json.dumps(deleted, indent=2))

    # 7) GET by id after delete should be 404
    resp = get_course_by_id(course_id)
    assert resp.status_code == 404, f"Expected 404 after delete, got {resp.status_code}"
    print("GET after delete correctly 404")

    # 8) Error scenarios (bad requests and not found)
    # 8a Missing required field (name)
    bad_post = {"description": "desc", "target_date": "2026-12-01", "status": "Not Started"}
    resp = post_course(bad_post)
    assert resp.status_code == 400, f"Bad POST (missing name) should 400, got {resp.status_code}"
    print("Bad POST (missing name) correctly 400")

    # 8b Invalid date
    bad_post = {"name": "BadDate", "description": "desc", "target_date": "2026-13-01", "status": "Not Started"}
    resp = post_course(bad_post)
    assert resp.status_code == 400, f"Bad POST (invalid date) should 400, got {resp.status_code}"
    print("Bad POST (invalid date) correctly 400")

    # 8c Invalid status
    bad_post = {"name": "BadStatus", "description": "desc", "target_date": "2026-12-01", "status": "Unknown"}
    resp = post_course(bad_post)
    assert resp.status_code == 400, f"Bad POST (invalid status) should 400, got {resp.status_code}"
    print("Bad POST (invalid status) correctly 400")

    # 8d PUT missing id
    bad_put = {"name": "NoID", "description": "desc", "target_date": "2026-12-01", "status": "Not Started"}
    resp = put_course(bad_put)
    assert resp.status_code == 400, f"Bad PUT (missing id) should 400, got {resp.status_code}"
    print("Bad PUT (missing id) correctly 400")

    # 8e DELETE missing id (empty body)
    resp = delete_course_by_body({})
    assert resp.status_code == 400, f"Bad DELETE (missing id) should 400, got {resp.status_code}"
    print("Bad DELETE (missing id) correctly 400")

    # 8f GET invalid id (non-numeric)
    resp = get_course_by_id("abc")
    assert resp.status_code in (400, 404), f"GET by invalid id should be 400/404, got {resp.status_code}"
    print("GET by invalid id correctly handled")

    # 8g GET not found (numeric id that doesn't exist)
    resp = get_course_by_id(999999)
    assert resp.status_code == 404, f"GET not found should be 404, got {resp.status_code}"
    print("GET not found correctly 404")

    # 8h DELETE not found
    resp = delete_course_by_id(999999)
    assert resp.status_code == 404, f"DELETE not found should be 404, got {resp.status_code}"
    print("DELETE not found correctly 404")

    print("All tests completed successfully.")

if __name__ == "__main__":
    run_tests()