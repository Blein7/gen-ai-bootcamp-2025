# Database Management

## Docker Environment (Recommended)

When using Docker (with `docker-compose up`), the database is automatically handled:

- The database file (`words.db`) is automatically created if it doesn't exist
- Schema migrations run automatically on container startup
- Seed data is loaded automatically
- The database is cleaned up when the container is shut down

This ensures a fresh state each time you start the application, which is ideal for development and testing.

## Manual Database Management

### Setting up the database

```sh
python init_db.py
```

This will do the following:
- Create the words.db (SQLite3 database)
- Run the migrations found in `sql/setup/`
- Load the seed data found in `seed/`

Please note that migrations and seed data are manually coded to be imported in the `lib/db.py`. If you want to import other seed data, you'll need to modify this code.

### Clearing the database

Simply delete the `words.db` file to clear the entire database:

```sh
rm words.db
```

### Database Location

The database is stored at the root of the backend folder as `words.db`. In the Docker environment, this path is `/app/words.db`.

## Running the backend API

With Docker (recommended):
```sh
docker-compose up
```

Manually:
```sh
python app.py 
```

This should start the Flask app on port `5000`

## Database Schema

The application uses several tables:
- `groups`: Word groups/categories
- `words`: Japanese vocabulary
- `word_groups`: Junction table connecting words and groups
- `study_activities`: Available study activities/exercises
- `study_sessions`: Records of user study sessions
- `word_reviews`: Tracking of word review records
- `word_review_items`: Individual words reviewed in a session
