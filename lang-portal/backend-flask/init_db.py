from app import create_app
from lib.db import db
import os

def main():
    print("Initializing database...")
    app = create_app()
    
    # Ensure database path is consistent
    with app.app_context():
        # First run migrations to ensure tables exist
        import sqlite3
        from migrate import run_migrations
        run_migrations()
        
        try:
            # Initialize database with seed data
            cursor = db.cursor()
            
            # Import word data
            db.import_word_json(
                cursor=cursor,
                group_name='Core Verbs',
                data_json_path='seed/data_verbs.json'
            )
            
            db.import_word_json(
                cursor=cursor,
                group_name='Core Adjectives',
                data_json_path='seed/data_adjectives.json'
            )
            
            # Import study activities
            db.import_study_activities_json(
                cursor=cursor,
                data_json_path='seed/study_activities.json'
            )
            
            print("Database initialization complete!")
        except Exception as e:
            print(f"Error during database initialization: {str(e)}")
            
if __name__ == "__main__":
    main() 