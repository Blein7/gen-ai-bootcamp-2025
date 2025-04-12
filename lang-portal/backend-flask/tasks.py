from invoke import task
from lib.db import db
import os

@task
def init_db(c=None):
  """Initialize the database
  This task can be run either as an invoke task with a Context or directly with None
  """
  from flask import Flask
  app = Flask(__name__)
  
  # Check for environment variable to override database path
  database_path = os.environ.get('DATABASE_PATH', 'instance/words.db')
  app.config['DATABASE'] = database_path
  
  print(f"Initializing database at: {database_path}")
  db.init(app)
  print("Database initialized successfully.")