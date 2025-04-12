# Backend API Routes for Frontend Integration

## Overview

This backend code was created to integrate missing API routes into an existing frontend. The work was based on a plan document (`study_sessions.md`), which outlined the necessary routes and their expected functionality. The goal was to fill in the missing routes and ensure smooth interaction with the frontend. Additionally, a test file was created to verify that all routes are working as expected.

## Technical Difficulties

While developing the backend, I encountered several challenges. The main issue was that the AI tool (Cursor) I used to help create the backend code often deviated from the plan specified in the `study_sessions.md` document. To overcome this, I had to constantly remind the tool to follow the plan/template and ensure that the code met the specifications.

Despite this issue, I was able to recreate the necessary backend API routes, test them, and integrate them with the frontend successfully.

## Docker Implementation

The backend is fully dockerized for easy deployment:

- **Automatic Database Initialization**: When the container starts for the first time, it automatically creates and initializes the `words.db` database with necessary schema and seed data via the Dockerfile.
- **Clean State on Restart**: The database is designed to be recreated on container restarts, ensuring a fresh state for development and testing.
- **Simple Deployment**: Just use `docker-compose up` to start the entire application stack.

### Docker Workflow

1. The Docker container uses an entrypoint script that checks if the database exists
2. If the database doesn't exist, it creates and initializes it with schema and seed data
3. The Flask application then starts and serves API requests
4. When the container shuts down, the database is automatically cleaned up

## Features

- **Missing API Routes Added**: The core task was to implement the missing API routes as outlined in the `study_sessions.md` document under plans.
- **Test File**: A comprehensive test file was added to verify the functionality of the newly implemented routes.
- **Integration**: Ensured the backend is fully integrated with the frontend codebase to enable seamless communication between the two.

## Development Environment

### Running with Docker (Recommended)

```sh
# From the project root directory:
docker-compose up
```

This starts both the backend and frontend containers. The backend will be available at http://localhost:5000.

### Running Locally (Without Docker)

To set up the database manually:

```sh
python init_db.py
```

To start the Flask application:

```sh
flask run --host=0.0.0.0 --port=5000
```

## Test Code

The tests codes are located in the tests folder

## Seed Data

The application includes sample study activities:

```json
[
  {
    "name": "Flashcards",
    "url": "http://localhost:3000/flashcards",
    "preview_url": "http://localhost:3000/flashcards/preview"
  },
  {
    "name": "Quiz",
    "url": "http://localhost:3000/quiz",
    "preview_url": "http://localhost:3000/quiz/preview"
  }
]
```

## Database Management

Please see the `DB_Readme.md` file for more detailed information about database operations.