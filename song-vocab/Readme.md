## Song Vocabulary Generator

This application extracts vocabulary from Japanese songs and provides translations and readings for language learners.

### Features
- Extracts lyrics from popular songs by artist and title
- Identifies key vocabulary
- Provides kanji, romaji, and English translations
- Saves results for future reference

## Running the Application

### Option 1: Using Docker Compose (Recommended)

The easiest way to run the application is using Docker Compose, which will automatically set up all dependencies:

1. From the root project directory:
```bash
docker-compose up -d song-vocab ollama
```

2. Wait for the services to initialize (Ollama needs to download the model, which might take a few minutes)

3. Test the API with:
```bash
curl -X POST http://localhost:8004/api/agent \
-H "Content-Type: application/json" \
-d '{
  "song_title": "Idol",
  "artist": "YOASOBI",
  "language": "Japanese"
}'
```

4. Output files will be created in the `song-vocab/output` directory:
   - `lyrics/{artist}_{song-title}_{language}.txt` - The lyrics of the song
   - `vocabulary/{artist}_{song-title}_{language}.json` - The vocabulary with translations

### Option 2: Using Docker Standalone

If you prefer to run just this component:

1. Build and run the Docker container:
```bash
cd song-vocab
docker build -t song-vocab .
docker run -p 8000:8000 -v ./output:/app/output song-vocab
```

2. Make sure you have Ollama running locally or specify the OLLAMA_HOST environment variable.

### Option 3: Running Locally

1. Install dependencies:
```bash
cd song-vocab
pip install -r requirements.txt
```

2. Make sure Ollama is running locally or set the OLLAMA_HOST environment variable.

3. Run the app:
```bash
python app.py
```

or with uvicorn:
```bash
uvicorn app:app --reload
```

4. Use the API as described above, but with port 8000 instead of 8004.

## Helper Scripts

You can also use the included script to make requests:
```bash
cd song-vocab
bash bin/post
```

## API Reference

### POST /api/agent
Create a new vocabulary extraction request.

**Request Body:**
```json
{
  "song_title": "string",
  "artist": "string",
  "language": "string"
}
```

**Response:**
```json
{
  "id": "string",
  "song_title": "string",
  "artist": "string",
  "language": "string",
  "lyrics": "string",
  "vocabulary": [
    {
      "word": "string",
      "reading": "string",
      "romaji": "string",
      "english": "string"
    }
  ],
  "source": "string"
}
```
