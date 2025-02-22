from datetime import datetime, UTC
from app import create_app

def init_test_data():
    app = create_app()
    with app.app_context():
        cursor = app.db.cursor()
        
        # Insert test group
        cursor.execute('''
            INSERT INTO groups (name, created_at)
            VALUES (?, ?)
        ''', ('Test Group', datetime.now(UTC)))
        
        # Insert test activity
        cursor.execute('''
            INSERT INTO study_activities (name, created_at)
            VALUES (?, ?)
        ''', ('Test Activity', datetime.now(UTC)))
        
        app.db.commit()
        print("Test data initialized successfully!")

if __name__ == '__main__':
    init_test_data() 