# Standard library imports
import pytest
import os
from datetime import datetime, UTC
import sqlite3
from flask.testing import FlaskClient
import sys

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from lib.db import Db

print("Test file is being loaded!")  # Debug print

# SQLite datetime handling setup
# These functions help SQLite properly store and retrieve datetime objects
def adapt_datetime(dt):
    """Convert datetime to ISO format string"""
    return dt.isoformat()

def convert_datetime(val):
    """Convert ISO format string back to datetime"""
    return datetime.fromisoformat(val)

# Register the custom datetime handlers with SQLite
sqlite3.register_adapter(datetime, adapt_datetime)
sqlite3.register_converter("datetime", convert_datetime)

# Database schema for testing
# Defines all the tables needed for the tests
TEST_DB_SCHEMA = '''
CREATE TABLE IF NOT EXISTS groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    created_at DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS study_activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    created_at DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS study_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    study_activity_id INTEGER NOT NULL,
    created_at DATETIME NOT NULL,
    FOREIGN KEY (group_id) REFERENCES groups(id),
    FOREIGN KEY (study_activity_id) REFERENCES study_activities(id)
);

CREATE TABLE IF NOT EXISTS word_review_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    study_session_id INTEGER NOT NULL,
    word_id INTEGER NOT NULL,
    correct INTEGER NOT NULL,
    created_at DATETIME NOT NULL,
    FOREIGN KEY (study_session_id) REFERENCES study_sessions(id)
);
'''

# Path for the test database file
TEST_DB_PATH = 'test_words.db'

# Module level setup - runs once before any tests
def setup_module(module):
    """Setup method that runs once before all tests"""
    print("\n=== Setting up test module ===")
    # Clean up any existing test database
    if os.path.exists(TEST_DB_PATH):
        os.unlink(TEST_DB_PATH)

# Module level teardown - runs once after all tests
def teardown_module(module):
    """Teardown method that runs once after all tests"""
    print("\n=== Cleaning up test module ===")
    # Clean up the test database
    if os.path.exists(TEST_DB_PATH):
        os.unlink(TEST_DB_PATH)

# Fixture to create and configure the Flask test application
@pytest.fixture
def app():
    """Create test app with fresh database for each test"""
    print("\nSetting up test app")  # Debug print
    test_app = create_app({
        'TESTING': True,
        'DATABASE': TEST_DB_PATH,
        'SQLITE_DATETIME': True  # Enable datetime handling
    })
    
    with test_app.app_context():
        cursor = test_app.db.cursor()
        cursor.executescript(TEST_DB_SCHEMA)
        cursor.execute('PRAGMA foreign_keys = ON;')
        test_app.db.commit()
        
        # Verify tables were created successfully
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"Created tables: {[table[0] for table in tables]}")
    
        yield test_app
    
        print("\nCleaning up test app")  # Debug print
        test_app.db.close()

# Fixture to create a test client for making requests
@pytest.fixture
def client(app):
    print("\nCreating test client")  # Debug print
    return app.test_client()

# Test successful creation of a study session
def test_create_study_session(client: FlaskClient, app):
    """Test successful creation of a study session"""
    print("\nRunning create test")
    with app.app_context():
        cursor = app.db.cursor()
        current_time = datetime.now(UTC)
        
        # Create test group
        cursor.execute('''
            INSERT INTO groups (name, created_at)
            VALUES (?, ?)
        ''', ('Test Group', current_time))
        group_id = cursor.lastrowid

        # Create test activity
        cursor.execute('''
            INSERT INTO study_activities (name, created_at)
            VALUES (?, ?)
        ''', ('Test Activity', current_time))
        activity_id = cursor.lastrowid

        app.db.commit()

        # Test creating session
        response = client.post('/api/study-sessions', json={
            'group_id': group_id,
            'study_activity_id': activity_id
        })

        # Print response data if there's an error
        if response.status_code != 201:
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.get_json()}")

        assert response.status_code == 201
        data = response.get_json()
        
        # Verify response data
        assert data['id'] is not None
        assert data['group_id'] == group_id
        assert data['group_name'] == 'Test Group'
        assert data['activity_id'] == activity_id
        assert data['activity_name'] == 'Test Activity'
        assert data['start_time'] is not None
        assert data['end_time'] is not None

# Test error handling for invalid inputs
def test_create_study_session_invalid_input(client: FlaskClient, app):
    """Test error cases for invalid inputs"""
    with app.app_context():
        # Test case 1: Missing all required fields
        response = client.post('/api/study-sessions', json={})
        assert response.status_code == 400
        assert response.get_json()['error'] == "group_id and study_activity_id are required"

        # Test case 2: Missing group_id field
        response = client.post('/api/study-sessions', json={
            'study_activity_id': 1
        })
        assert response.status_code == 400
        assert response.get_json()['error'] == "group_id and study_activity_id are required"

        # Test case 3: Missing study_activity_id field
        response = client.post('/api/study-sessions', json={
            'group_id': 1
        })
        assert response.status_code == 400
        assert response.get_json()['error'] == "group_id and study_activity_id are required"

        # Test case 4: Invalid IDs (IDs that don't exist in database)
        response = client.post('/api/study-sessions', json={
            'group_id': 99999,
            'study_activity_id': 99999
        })
        assert response.status_code == 400
        assert response.get_json()['error'] in ["Invalid group_id", "Invalid group_id or study_activity_id"]

def test_get_study_sessions(client: FlaskClient, app):
    """Test getting all study sessions"""
    with app.app_context():
        # Create test data first
        cursor = app.db.cursor()
        current_time = datetime.now(UTC)
        
        # Create test group and activity
        cursor.execute('INSERT INTO groups (name, created_at) VALUES (?, ?)', 
                      ('Test Group', current_time))
        group_id = cursor.lastrowid

        cursor.execute('INSERT INTO study_activities (name, created_at) VALUES (?, ?)', 
                      ('Test Activity', current_time))
        activity_id = cursor.lastrowid

        # Create test session
        cursor.execute('''
            INSERT INTO study_sessions (group_id, study_activity_id, created_at)
            VALUES (?, ?, ?)
        ''', (group_id, activity_id, current_time))
        app.db.commit()

        # Test GET endpoint
        response = client.get('/api/study-sessions')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'items' in data
        assert len(data['items']) > 0
        assert data['total'] > 0

        # Verify first session data
        session = data['items'][0]
        assert session['group_id'] == group_id
        assert session['group_name'] == 'Test Group'
        assert session['activity_id'] == activity_id
        assert session['activity_name'] == 'Test Activity' 