from flask import Blueprint, request, jsonify, g
from flask_cors import cross_origin
from datetime import datetime, UTC
import math
from lib.db import db

bp = Blueprint('study_sessions', __name__)

@bp.route('/api/study-sessions', methods=['POST'])
@cross_origin()
def create_study_session():
    try:
        data = request.get_json()
        print(f"Received data: {data}")  # Debug print
        
        # Validate input data
        if not data or not data.get('group_id') or not data.get('study_activity_id'):
            return jsonify({"error": "group_id and study_activity_id are required"}), 400

        cursor = db.cursor()
        
        # Verify group_id and study_activity_id exist
        cursor.execute('SELECT id FROM groups WHERE id = ?', (data['group_id'],))
        group = cursor.fetchone()
        print(f"Found group: {group}")  # Debug print
        
        if not group:
            return jsonify({"error": "Invalid group_id"}), 400
            
        cursor.execute('SELECT id FROM study_activities WHERE id = ?', (data['study_activity_id'],))
        activity = cursor.fetchone()
        print(f"Found activity: {activity}")  # Debug print
        
        if not activity:
            return jsonify({"error": "Invalid study_activity_id"}), 400

        # Insert new study session
        try:
            cursor.execute('''
                INSERT INTO study_sessions (group_id, study_activity_id, created_at)
                VALUES (?, ?, datetime('now'))
            ''', (data['group_id'], data['study_activity_id']))
            db.commit()
            print(f"Inserted new session with id: {cursor.lastrowid}")  # Debug print
        except Exception as insert_error:
            print(f"Insert error: {insert_error}")  # Debug print
            raise

        new_id = cursor.lastrowid

        # Fetch complete session details
        try:
            cursor.execute('''
                SELECT 
                    ss.id, 
                    ss.group_id, 
                    g.name as group_name,
                    sa.id as activity_id, 
                    sa.name as activity_name,
                    datetime(ss.created_at) as created_at
                FROM study_sessions ss
                JOIN groups g ON g.id = ss.group_id
                JOIN study_activities sa ON sa.id = ss.study_activity_id
                WHERE ss.id = ?
            ''', (new_id,))
            session = cursor.fetchone()
            print(f"Fetched session details: {session}")  # Debug print
        except Exception as fetch_error:
            print(f"Fetch error: {fetch_error}")  # Debug print
            raise

        if not session:
            return jsonify({"error": "Failed to fetch created session"}), 500

        return jsonify({
            'id': session['id'],
            'group_id': session['group_id'],
            'group_name': session['group_name'],
            'activity_id': session['activity_id'],
            'activity_name': session['activity_name'],
            'start_time': session['created_at'],
            'end_time': session['created_at']
        }), 201
        
    except Exception as e:
        print(f"Error in create_study_session: {str(e)}")  # Debug print
        return jsonify({"error": str(e)}), 500

@bp.route('/api/study-sessions', methods=['GET'])
@cross_origin()
def get_study_sessions():
    try:
        cursor = db.cursor()
        
        cursor.execute('''
            SELECT 
                ss.id,
                ss.group_id,
                g.name as group_name,
                sa.id as activity_id,
                sa.name as activity_name,
                datetime(ss.created_at) as created_at
            FROM study_sessions ss
            JOIN groups g ON g.id = ss.group_id
            JOIN study_activities sa ON sa.id = ss.study_activity_id
            ORDER BY ss.created_at DESC
        ''')
        sessions = cursor.fetchall()
        
        # Convert to list of dicts
        result = []
        if sessions:
            for session in sessions:
                try:
                    session_dict = dict(session)
                    # Add start_time and end_time using created_at
                    session_dict['start_time'] = session_dict['created_at']
                    session_dict['end_time'] = session_dict['created_at']
                    result.append(session_dict)
                except Exception as conv_error:
                    print(f"Conversion error: {conv_error}")
                    continue
        
        return jsonify({
            'items': result,
            'total': len(result),
            'page': 1,
            'per_page': 10,
            'total_pages': 1
        })
    except Exception as e:
        import traceback
        return jsonify({
            "error": str(e),
            "type": str(type(e)),
            "detail": "Error in get_study_sessions",
            "traceback": traceback.format_exc()
        }), 500

@bp.route('/api/study-sessions/<int:id>', methods=['GET'])
@cross_origin()
def get_study_session(id):
    try:
        cursor = db.cursor()
        cursor.execute('''
            SELECT 
                ss.id,
                ss.group_id,
                g.name as group_name,
                sa.id as activity_id,
                sa.name as activity_name,
                datetime(ss.created_at) as created_at
            FROM study_sessions ss
            JOIN groups g ON g.id = ss.group_id
            JOIN study_activities sa ON sa.id = ss.study_activity_id
            WHERE ss.id = ?
        ''', (id,))
        session = cursor.fetchone()
        
        if session is None:
            return jsonify({'error': 'Study session not found'}), 404
            
        result = dict(session)
        # Add start_time and end_time using created_at
        result['start_time'] = result['created_at']
        result['end_time'] = result['created_at']
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/study-sessions/<int:id>', methods=['PUT'])
@cross_origin()
def update_study_session(id):
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'start_time', 'end_time', 'language']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
                
        cursor = db.cursor()
        cursor.execute('''
            UPDATE study_sessions 
            SET title = ?, description = ?, start_time = ?, end_time = ?, language = ?
            WHERE id = ?
        ''', (
            data['title'],
            data.get('description', ''),
            data['start_time'],
            data['end_time'],
            data['language'],
            id
        ))
        db.commit()
        
        if cursor.rowcount == 0:
            return jsonify({'error': 'Study session not found'}), 404
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/study-sessions/<int:id>', methods=['DELETE'])
@cross_origin()
def delete_study_session(id):
    try:
        cursor = db.cursor()
        cursor.execute('DELETE FROM study_sessions WHERE id = ?', (id,))
        db.commit()
        
        if cursor.rowcount == 0:
            return jsonify({'error': 'Study session not found'}), 404
        return '', 204
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/study-sessions/reset', methods=['POST'])
@cross_origin()
def reset_study_sessions():
    try:
        cursor = db.cursor()
        cursor.execute('DELETE FROM study_sessions')
        db.commit()
        return jsonify({"message": "Study history cleared successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/study-sessions/debug', methods=['GET'])
@cross_origin()
def debug_study_sessions():
    try:
        cursor = db.cursor()
        
        # Check if table exists
        cursor.execute('''
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='study_sessions';
        ''')
        table_exists = cursor.fetchone()
        
        if not table_exists:
            return jsonify({"error": "study_sessions table does not exist"}), 500
            
        # Get table info
        cursor.execute('PRAGMA table_info(study_sessions);')
        columns = cursor.fetchall()
        
        return jsonify({
            "table_exists": True,
            "columns": [dict(col) for col in columns]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def load(app):
    app.register_blueprint(bp)