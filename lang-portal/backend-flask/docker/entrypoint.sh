#!/bin/bash

# Check database location
echo "Checking database location..."

# Remove any existing database file in the instance directory
if [ -f /app/instance/words.db ]; then
  echo "Found database file in instance directory, removing..."
  rm -f /app/instance/words.db
fi

# Check if database exists in root directory
if [ ! -f /app/words.db ]; then
  echo "Database does not exist. Creating and initializing..."
  
  # Create empty database file in root directory
  touch /app/words.db
  chmod 666 /app/words.db
  
  # Run database initialization
  python init_db.py
  
  # Check if initialization was successful
  if [ $? -ne 0 ]; then
    echo "Database initialization failed!"
    exit 1
  fi
  
  echo "Database successfully created and initialized at /app/words.db"
else
  echo "Database already exists at /app/words.db. Skipping initialization."
fi

# Start Flask application
echo "Starting Flask application..."
exec flask run --host=0.0.0.0 --port=5000 