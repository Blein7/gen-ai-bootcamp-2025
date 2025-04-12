# Japanese Writing Practice

This application helps you practice writing Japanese by providing sentences to write, OCR recognition of your handwriting, and automatic grading.

## Running the Application

### Using Docker (Recommended)

The simplest way to run this application is using Docker:

```bash
# From the project root directory:
docker-compose up writing-practice lang-portal-backend lang-portal-frontend
```

This will start:
- The Writing Practice app at http://localhost:8503
- The backend API at http://localhost:5000
- The frontend UI at http://localhost:3000

### Without Docker

If you want to run without Docker:

1. Make sure you have Python 3.9+ installed
2. Install dependencies: `pip install -r requirements.txt`
3. Set your OpenAI API key in the `.env` file
4. Run the app: `streamlit run app.py`

## How to Use

1. **Access the Application**:
   - Open your browser and go to http://localhost:8503

2. **Provide a Group ID**:
   - The app requires a group ID parameter in the URL
   - Example: http://localhost:8503?group_id=1

3. **Practice Writing**:
   - You'll be presented with an English sentence
   - Write the sentence in Japanese on paper
   - Take a photo or screenshot of your writing
   - Upload the image
   - Submit for review

4. **View the Feedback**:
   - The app will show you:
     - Transcription of your handwriting
     - Translation of your Japanese
     - Score and feedback on your writing

## Viewing Your Practice History

All of your writing practice sessions are recorded in the Lang Portal application. To view your practice history:

1. Go to http://localhost:3000/sessions
2. By default, you'll only see Writing Practice sessions
3. Each session shows:
   - The date and time of your practice
   - The word group you practiced with
   - Correct/incorrect count

You can click on any session to see details of the specific words you practiced.

## Technical Details

- The application uses MangaOCR for Japanese text recognition
- OpenAI's API is used for translation and grading
- All practice data is stored in the Lang Portal backend database
- Sessions are filtered in the frontend to show only Writing Practice activities

## Requirements

- OpenAI API key (set in the `.env` file)
- Camera or screenshot capability for uploading handwriting
- Modern web browser

For more detailed technical specifications, see the `Tech-specs.md` file. 