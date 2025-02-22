# Plan to Implement POST /api/study-sessions

This plan outlines the steps required to implement the `POST` endpoint for `/api/study-sessions`. The goal is to create a new study session, insert it into the database, and return the created session's details.

### Steps

1. **Define the POST route** for `/api/study-sessions`
    - [x] Create a new route for `POST /api/study-sessions` in the Flask app.
    - [x] Use `@app.route('/api/study-sessions', methods=['POST'])` decorator.
    - [x] Add `@cross_origin()` to support CORS if needed.

2. **Parse JSON data from the request**  
    - [x] Extract the JSON payload from the request using `request.get_json()`.
    - [x] Validate the data to ensure required fields are present (e.g., `group_id`, `study_activity_id`, etc.).
    - [x] If required data is missing, return a `400 Bad Request` response with an error message.

3. **Insert the new study session into the database**  
    - [x] Use the `INSERT INTO study_sessions` SQL query to insert a new record into the `study_sessions` table.
    - [x] Ensure that the `group_id` and `study_activity_id` are valid by checking if they exist in the respective tables (`groups` and `study_activities`).
    - [x] If the insertion is successful, commit the transaction to the database.

4. **Return the created session in the response**  
    - [x] After inserting the study session, fetch the session details (ID, group name, activity name, etc.) and return them in the response.
    - [x] Return the response with status `201 Created` and the newly created study session's details.

5. **Handle exceptions**  
    - [x] Wrap the code in a `try-except` block to catch and handle any exceptions (e.g., database errors, invalid data).
    - [x] Return a `500 Internal Server Error` response with the error message if an exception is raised.

6. **Testing the endpoint**  
    - [x] Write unit tests for this endpoint.
    - [x] Use Flask's test client (`app.test_client()`) to simulate `POST` requests.
    - [x] Check that the session is created successfully and the response status is `201`.
    - [x] Validate that the correct data is returned in the response (e.g., session ID, group name, activity name).

---

### Example Code for the Implementation

```python
@app.route('/api/study-sessions', methods=['POST'])
@cross_origin()
def create_study_session():
    try:
        data = request.get_json()
        
        # Validate input data
        if not data or not data.get('group_id') or not data.get('study_activity_id'):
            return jsonify({"error": "group_id and study_activity_id are required"}), 400

        # Insert new study session into the database
        cursor = app.db.cursor()
        cursor.execute('''
            INSERT INTO study_sessions (group_id, study_activity_id, created_at)
            VALUES (?, ?, ?)
        ''', (data['group_id'], data['study_activity_id'], datetime.utcnow()))
        app.db.commit()

        # Get the ID of the newly inserted session
        cursor.execute('SELECT LAST_INSERT_ID()')
        new_session_id = cursor.fetchone()[0]

        # Fetch the details of the newly created session
        cursor.execute('''
            SELECT ss.id, ss.group_id, g.name as group_name, sa.id as activity_id, sa.name as activity_name, ss.created_at
            FROM study_sessions ss
            JOIN groups g ON g.id = ss.group_id
            JOIN study_activities sa ON sa.id = ss.study_activity_id
            WHERE ss.id = ?
        ''', (new_session_id,))
        session = cursor.fetchone()

        return jsonify({
            'id': session['id'],
            'group_id': session['group_id'],
            'group_name': session['group_name'],
            'activity_id': session['activity_id'],
            'activity_name': session['activity_name'],
            'start_time': session['created_at'],
            'end_time': session['created_at'],  # For now, just use the same time
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
