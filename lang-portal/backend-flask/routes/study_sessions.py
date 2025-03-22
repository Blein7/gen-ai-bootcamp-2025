from flask import request, jsonify, g
from flask_cors import cross_origin
from datetime import datetime
import math

def load(app):
  # todo /study_sessions POST, code added
  @app.route('/api/study-sessions', methods=['POST'])
  @cross_origin()
  def create_study_session():
      try:
          data = request.get_json()
          group_id = data['group_id']
          activity_id = data['activity_id']
          created_at = datetime.now()

          cursor = app.db.cursor()
          cursor.execute('''
              INSERT INTO study_sessions (group_id, study_activity_id, created_at)
              VALUES (?, ?, ?)
          ''', (group_id, activity_id, created_at))
          session_id = cursor.lastrowid
          app.db.commit()

          return jsonify({"session_id": session_id}), 201
      except Exception as e:
          return jsonify({"error": str(e)}), 500

  @app.route('/api/study-sessions', methods=['GET'])
  @cross_origin()
  def get_study_sessions():
    try:
      cursor = app.db.cursor()
      
      # Get pagination parameters
      page = request.args.get('page', 1, type=int)
      per_page = request.args.get('per_page', 10, type=int)
      offset = (page - 1) * per_page

      # Get total count
      cursor.execute('''
        SELECT COUNT(*) as count 
        FROM study_sessions ss
        JOIN groups g ON g.id = ss.group_id
        JOIN study_activities sa ON sa.id = ss.study_activity_id
      ''')
      total_count = cursor.fetchone()['count']

      # Get paginated sessions
      cursor.execute('''
        SELECT 
          ss.id,
          ss.group_id,
          g.name as group_name,
          sa.id as activity_id,
          sa.name as activity_name,
          ss.created_at,
          COUNT(wri.id) as review_items_count,
          SUM(CASE WHEN wri.correct = 1 THEN 1 ELSE 0 END) as correct_count,
          SUM(CASE WHEN wri.correct = 0 THEN 1 ELSE 0 END) as wrong_count
        FROM study_sessions ss
        JOIN groups g ON g.id = ss.group_id
        JOIN study_activities sa ON sa.id = ss.study_activity_id
        LEFT JOIN word_review_items wri ON wri.study_session_id = ss.id
        GROUP BY ss.id
        ORDER BY ss.created_at DESC
        LIMIT ? OFFSET ?
      ''', (per_page, offset))
      sessions = cursor.fetchall()

      return jsonify({
        'items': [{
          'id': session['id'],
          'group_id': session['group_id'],
          'group_name': session['group_name'],
          'activity_id': session['activity_id'],
          'activity_name': session['activity_name'],
          'start_time': session['created_at'],
          'end_time': session['created_at'],  # For now, just use the same time since we don't track end time
          'review_items_count': session['review_items_count'],
          'correct_count': session['correct_count'] or 0,
          'wrong_count': session['wrong_count'] or 0
        } for session in sessions],
        'total': total_count,
        'page': page,
        'per_page': per_page,
        'total_pages': math.ceil(total_count / per_page)
      })
    except Exception as e:
      return jsonify({"error": str(e)}), 500

  @app.route('/api/study-sessions/<int:id>', methods=['GET'])
  @cross_origin()
  def get_study_session(id):
    try:
      cursor = app.db.cursor()
      print(f"Fetching study session {id}")  # Debug log
      
      # Get session details
      cursor.execute('''
        SELECT 
          ss.id,
          ss.group_id,
          g.name as group_name,
          sa.id as activity_id,
          sa.name as activity_name,
          ss.created_at,
          COUNT(wri.id) as review_items_count,
          SUM(CASE WHEN wri.correct = 1 THEN 1 ELSE 0 END) as correct_count,
          SUM(CASE WHEN wri.correct = 0 THEN 1 ELSE 0 END) as wrong_count
        FROM study_sessions ss
        JOIN groups g ON g.id = ss.group_id
        JOIN study_activities sa ON sa.id = ss.study_activity_id
        LEFT JOIN word_review_items wri ON wri.study_session_id = ss.id
        WHERE ss.id = ?
        GROUP BY ss.id
      ''', (id,))
      
      session = cursor.fetchone()
      print(f"Session data: {dict(session) if session else None}")  # Debug log
      
      if not session:
        print(f"Study session {id} not found")  # Debug log
        return jsonify({"error": "Study session not found"}), 404

      # Get pagination parameters
      page = request.args.get('page', 1, type=int)
      per_page = request.args.get('per_page', 10, type=int)
      offset = (page - 1) * per_page

      print(f"Fetching words for session {id}")  # Debug log
      # Get the words reviewed in this session with their review status
      cursor.execute('''
        SELECT 
          w.*,
          COALESCE(SUM(CASE WHEN wri.correct = 1 THEN 1 ELSE 0 END), 0) as correct_count,
          COALESCE(SUM(CASE WHEN wri.correct = 0 THEN 1 ELSE 0 END), 0) as wrong_count
        FROM words w
        JOIN word_review_items wri ON wri.word_id = w.id
        WHERE wri.study_session_id = ?
        GROUP BY w.id
        ORDER BY w.kanji
        LIMIT ? OFFSET ?
      ''', (id, per_page, offset))
      
      words = cursor.fetchall()
      print(f"Found {len(words)} words")  # Debug log

      # Get total count of words
      cursor.execute('''
        SELECT COUNT(DISTINCT w.id) as count
        FROM words w
        JOIN word_review_items wri ON wri.word_id = w.id
        WHERE wri.study_session_id = ?
      ''', (id,))
      
      total_count = cursor.fetchone()['count']
      print(f"Total words count: {total_count}")  # Debug log

      response_data = {
        'session': {
          'id': session['id'],
          'group_id': session['group_id'],
          'group_name': session['group_name'],
          'activity_id': session['activity_id'],
          'activity_name': session['activity_name'],
          'start_time': session['created_at'],
          'end_time': session['created_at'],  # For now, just use the same time
          'review_items_count': session['review_items_count'],
          'correct_count': session['correct_count'] or 0,
          'wrong_count': session['wrong_count'] or 0
        },
        'words': [{
          'id': word['id'],
          'kanji': word['kanji'],
          'romaji': word['romaji'],
          'english': word['english'],
          'correct_count': word['correct_count'],
          'wrong_count': word['wrong_count']
        } for word in words],
        'total': total_count,
        'page': page,
        'per_page': per_page,
        'total_pages': math.ceil(total_count / per_page)
      }
      print(f"Sending response: {response_data}")  # Debug log
      return jsonify(response_data)
    except Exception as e:
      print(f"Error in get_study_session: {str(e)}")  # Debug log
      return jsonify({"error": str(e)}), 500

  # todo POST /study_sessions/:id/review, code added

  @app.route('/api/study-sessions/<int:id>/review', methods=['POST'])
  @cross_origin()
  def add_review_item(id):
      try:
          cursor = app.db.cursor()
          
          # Check if study session exists
          cursor.execute('SELECT id FROM study_sessions WHERE id = ?', (id,))
          session = cursor.fetchone()
          
          # If session doesn't exist, create it
          if not session:
              # Get the group_id from the word being reviewed
              data = request.get_json()
              word_id = data['word_id']
              cursor.execute('SELECT group_id FROM word_groups WHERE word_id = ? LIMIT 1', (word_id,))
              group = cursor.fetchone()
              if not group:
                  return jsonify({"error": "Word not found in any group"}), 404
                  
              # Create study session
              cursor.execute('''
                  INSERT INTO study_sessions (id, group_id, study_activity_id, created_at)
                  VALUES (?, ?, ?, ?)
              ''', (id, group['group_id'], 2, datetime.now()))  # study_activity_id 2 is "Writing Practice"
              app.db.commit()

          # Add the review item
          data = request.get_json()
          word_id = data['word_id']
          correct = data['correct']
          created_at = datetime.now()

          cursor.execute('''
              INSERT INTO word_review_items (study_session_id, word_id, correct, created_at)
              VALUES (?, ?, ?, ?)
          ''', (id, word_id, correct, created_at))
          app.db.commit()

          return jsonify({"message": "Review item added successfully"}), 201
      except Exception as e:
          return jsonify({"error": str(e)}), 500

  @app.route('/api/study-sessions/reset', methods=['POST'])
  @cross_origin()
  def reset_study_sessions():
    try:
      cursor = app.db.cursor()
      
      # First delete all word review items since they have foreign key constraints
      cursor.execute('DELETE FROM word_review_items')
      
      # Then delete all study sessions
      cursor.execute('DELETE FROM study_sessions')
      
      app.db.commit()
      
      return jsonify({"message": "Study history cleared successfully"}), 200
    except Exception as e:
      return jsonify({"error": str(e)}), 500

  @app.route('/api/debug/tables', methods=['GET'])
  @cross_origin()
  def list_tables():
    try:
      cursor = app.db.cursor()
      
      # Get list of tables
      cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
      tables = cursor.fetchall()
      
      result = {}
      for table in tables:
        table_name = table['name']
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
        rows = cursor.fetchall()
        # Convert Row objects to dictionaries
        result[table_name] = [dict(row) for row in rows]
        
      return jsonify(result)
    except Exception as e:
      return jsonify({"error": str(e)}), 500

  @app.route('/api/debug/fix-session', methods=['POST'])
  @cross_origin()
  def fix_session():
    try:
      cursor = app.db.cursor()
      
      # Get the first word_review_item to get study_session_id and word_id
      cursor.execute('SELECT study_session_id, word_id FROM word_review_items LIMIT 1')
      review = cursor.fetchone()
      if not review:
        return jsonify({"error": "No review items found"}), 404
        
      # Get the group_id for this word
      cursor.execute('SELECT group_id FROM word_groups WHERE word_id = ?', (review['word_id'],))
      group = cursor.fetchone()
      if not group:
        return jsonify({"error": "Word not found in any group"}), 404
        
      # Create the missing study session
      cursor.execute('''
        INSERT INTO study_sessions (id, group_id, study_activity_id, created_at)
        VALUES (?, ?, ?, ?)
      ''', (review['study_session_id'], group['group_id'], 2, datetime.now()))
      app.db.commit()
      
      return jsonify({"message": "Study session created successfully"}), 201
    except Exception as e:
      return jsonify({"error": str(e)}), 500