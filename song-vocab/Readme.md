## How to run the fastapi app

1. Install dependencies:
```bash
pip install -r requirements.txt
```
2. Run the app:
```bash
python app.py
```

or with uvicorn:
```bash
uvicorn app:app --reload
```

3. Use this curl command to test the API:
```bash
curl -X POST http://localhost:8000/api/agent \
-H "Content-Type: application/json" \
-d '{
  "song_title": "Idol",
  "artist": "YOASOBI",
  "language": "Japanese"
}'
```

4. The app will process the request and generate output files in the `output` directory.

5. The output files will be:
- `lyrics/{identifier}.txt` - The lyrics of the song
- `vocabulary/{identifier}.json` - The vocabulary extracted from the lyrics

6. You can also use the `bin/post` script to make requests:
```bash
python bin/post.py
```
