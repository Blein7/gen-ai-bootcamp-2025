import streamlit as st
# Must be the first Streamlit command
st.set_page_config(
    page_title="Japanese Writing Practice",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

import requests
import random
import os
import io
import logging
import numpy as np
from PIL import Image
import cv2
import openai
from manga_ocr import MangaOcr
from dotenv import load_dotenv
from streamlit_drawable_canvas import st_canvas
import datetime
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Initialize PyTorch after Streamlit configuration
import warnings
with warnings.catch_warnings():
    warnings.filterwarnings('ignore', category=UserWarning)
    import torch
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    torch.set_grad_enabled(False)

# Load environment variables from .env file
load_dotenv()

# Constants for application states
SETUP = "setup"
PRACTICE = "practice"
REVIEW = "review"

# Initialize OCR model at module level
mocr = None
try:
    from manga_ocr import MangaOcr
    mocr = MangaOcr()
    print("OCR model initialized successfully")
except Exception as e:
    print(f"Error initializing OCR model: {str(e)}")

def init_mocr():
    """Get the initialized OCR model"""
    global mocr
    return mocr

@st.cache_data
def process_image_with_ocr(image_bytes):
    """Process image with OCR using global model"""
    global mocr
    if mocr is None:
        return "Error: OCR model not initialized"
    
    try:
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Process with OCR
        text = mocr(image)
        print(f"OCR Result: {text}")
        return text
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return "Error processing image"

# Configure OpenAI API
openai.api_key = os.getenv('OPENAI_API_KEY')
print(f"API Key found: {'Yes' if openai.api_key else 'No'}")  # Debug print
print(f"API Key length: {len(openai.api_key) if openai.api_key else 0}")  # Debug print

if not openai.api_key or openai.api_key == "your_api_key_here":
    error_msg = """
    OpenAI API key not found! Please set your OPENAI_API_KEY environment variable.
    
    You can do this by:
    1. Opening the .env file in the writing-practice directory
    2. Replacing 'your_api_key_here' with your actual OpenAI API key
    """
    st.error(error_msg)
    st.stop()

# Get query parameters
def get_session_id():
    """Get session ID and group ID from URL parameters"""
    try:
        # Get group_id from URL params
        group_id = st.query_params.get("group_id")
        
        # Group ID is required
        if not group_id:
            st.error("Missing group_id in URL. Please access this app through the main portal.")
            return None, None
            
        # Convert to integer
        try:
            group_id = int(group_id)
        except (ValueError, TypeError):
            st.error("Invalid group_id. Must be a number.")
            return None, None
        
        # Get or create session ID
        session_id = st.query_params.get("session_id")
        if not session_id:
            try:
                # Create new session
                response = requests.post(
                    "http://localhost:5000/api/study-sessions",
                    json={
                        "group_id": group_id,
                        "activity_id": 2  # Writing Practice activity
                    }
                )
                if response.ok:
                    session_data = response.json()
                    session_id = session_data.get("id")
                    if session_id:
                        # Update URL without refreshing
                        st.query_params["group_id"] = str(group_id)
                        st.query_params["session_id"] = str(session_id)
                    else:
                        st.error("Invalid response from server when creating session")
                        return None, None
                else:
                    st.error(f"Failed to create study session: {response.text}")
                    return None, None
            except Exception as e:
                logging.error(f"Error creating session: {str(e)}")
                st.error("Error creating study session")
                return None, None
        else:
            try:
                session_id = int(session_id)
            except (ValueError, TypeError):
                st.error("Invalid session_id. Must be a number.")
                return None, None
        
        logging.info(f"Query params - session_id: {session_id}, group_id: {group_id}")
        return session_id, group_id
    except Exception as e:
        logging.error(f"Error getting session/group ID: {str(e)}")
        st.error("Error getting session/group ID. Please access this app through the main portal.")
        return None, None

def fetch_words(group_id, session_id=None):
    """Fetch words from API"""
    try:
        # Ensure we have a valid group ID
        if group_id is None:
            logging.error("Cannot fetch words: group_id is None")
            return None
            
        # Just fetch words from the backend API
        url = f"http://localhost:5000/groups/{group_id}/words/raw"
        logging.info(f"Fetching words from: {url}")
        response = requests.get(url, headers={'Accept': 'application/json'})
        
        if response.ok:
            try:
                data = response.json()
                logging.info(f"Response content type: {response.headers.get('content-type')}")
                logging.info(f"Raw response text: {response.text[:1000]}")  # Log first 1000 chars
                
                # Check if we have words in the response
                if not isinstance(data, dict) or 'words' not in data:
                    logging.error(f"Invalid response format: {data}")
                    return None
                    
                words_data = data['words']
                if not isinstance(words_data, list):
                    logging.error(f"Words data is not a list: {words_data}")
                    return None
                    
                # Transform words to include ID
                words = []
                for word in words_data:
                    try:
                        words.append({
                            'id': word['id'],
                            'kanji': word['kanji'],
                            'romaji': word['romaji'],
                            'english': word['english']
                        })
                    except KeyError as e:
                        logging.error(f"Missing key in word data: {e}, word: {word}")
                        continue
                    
                if not words:
                    logging.error("No valid words found after transformation")
                    return None
                    
                logging.info(f"Successfully transformed {len(words)} words")
                return words
            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse JSON response: {e}")
                return None
        else:
            logging.error(f"Failed to fetch words. Status: {response.status_code}, Response: {response.text}")
            st.error(f"Failed to fetch words. Status code: {response.status_code}")
            return None
    except Exception as e:
        logging.error(f"Error fetching words: {str(e)}")
        st.error(f"Error fetching words: {str(e)}")
        return None

def call_gpt(prompt, system_prompt=None, temperature=0.7):
    """Call GPT with the given prompt"""
    try:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        print(f"Making OpenAI API call with messages: {messages}")  # Debug print
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Using GPT-4 model
            messages=messages,
            temperature=temperature,
            max_tokens=500  # Limiting response length for cost efficiency
        )
        print(f"OpenAI API response: {response}")  # Debug print
        return response.choices[0].message.content
    except Exception as e:
        error_msg = f"Error calling GPT: {str(e)}"
        print(f"OpenAI API Error: {error_msg}")  # Debug print
        st.error(error_msg)  # Show in UI
        return None

def generate_sentence(word):
    """Generate a sentence using the provided word"""
    system_prompt = """You are a Japanese language teacher. Generate a simple Japanese sentence using the provided word.
    Follow these rules:
    1. Use only JLPT N5 level grammar
    2. Use common vocabulary that beginners would know
    3. Keep the sentence short and practical
    4. Return ONLY the Japanese sentence, no explanations or translations"""
    
    prompt = f"""Generate a simple Japanese sentence using the word: {word['kanji']} ({word['romaji']}) which means '{word['english']}'.
    The sentence should be something practical that you might use in daily life."""
    
    japanese_sentence = call_gpt(prompt, system_prompt, temperature=0.7)
    if not japanese_sentence:
        return f"私は{word['kanji']}が好きです。"
    return japanese_sentence

def translate_text(text):
    """Simple mock translation for demo purposes"""
    # For demo, just return the text as is
    return text

def preprocess_image(img):
    """Preprocess image for better OCR recognition"""
    try:
        print(f"Starting image preprocessing. Image info: size={img.size}, mode={img.mode}")
        
        # Convert to RGB if not already
        if img.mode != 'RGB':
            print(f"Converting image from {img.mode} to RGB")
            img = img.convert('RGB')
        
        # Convert to grayscale
        print("Converting to grayscale")
        img = img.convert('L')
        
        # Convert to numpy array
        print("Converting to numpy array")
        img_array = np.array(img)
        print(f"Array shape: {img_array.shape}, dtype: {img_array.dtype}")
        
        # Normalize and enhance contrast
        print("Enhancing contrast")
        if img_array.max() == img_array.min():
            raise ValueError("Image has no contrast")
            
        img_array = ((img_array - img_array.min()) * (255.0 / (img_array.max() - img_array.min()))).astype('uint8')
        
        # Convert back to PIL Image
        print("Converting back to PIL Image")
        img = Image.fromarray(img_array)
        
        # Resize to appropriate size
        print("Resizing image")
        target_height = 700
        aspect_ratio = img.width / img.height
        target_width = int(target_height * aspect_ratio)
        img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
        print(f"Final image size: {img.size}")
        
        return img
    except Exception as e:
        print(f"Error in preprocess_image: {str(e)}")
        raise

def grade_attempt(word, transcription):
    """Grade the attempt and submit review to backend"""
    # Determine if the attempt is correct
    is_correct = (transcription == word['kanji'])
    
    try:
        # Store review locally
        if 'reviews' not in st.session_state:
            st.session_state.reviews = []
        
        review = {
            "word_id": word['id'],
            "correct": is_correct,
            "group_id": st.session_state.group_id,
            "timestamp": str(datetime.datetime.now())
        }
        st.session_state.reviews.append(review)
        print(f"Created review: {review}")
        
        try:
            # Get session ID from session state
            session_id = st.session_state.session_id
            print(f"Using session_id: {session_id}")
            
            if not session_id:
                logging.error("No session_id found in session state")
                return "Warning", "No session ID found - review not saved"
            
            # Submit review to backend
            review_data = {
                "word_id": int(word['id']),
                "correct": bool(is_correct)
            }
            print(f"Submitting review to backend: {review_data}")
            
            response = requests.post(
                f"http://localhost:5000/api/study-sessions/{session_id}/review",
                json=review_data
            )
            print(f"Backend response status: {response.status_code}")
            print(f"Backend response text: {response.text}")
            
            if not response.ok:
                logging.error(f"Error submitting review to backend: {response.text}")
                return "Warning", "Failed to save review to backend"
                
        except Exception as e:
            logging.error(f"Error submitting review to backend: {str(e)}")
            return "Warning", "Error saving review"
        
        # Generate feedback
        if is_correct:
            grade = "Success"
            feedback = "✅ Correct! Your writing matches the kanji."
        else:
            grade = "Warning"
            feedback = f"❌ Not quite. The correct kanji is: {word['kanji']}"
        
        return grade, feedback
    except Exception as e:
        logging.error(f"Error in grade_attempt: {str(e)}")
        st.error(f"Error grading attempt: {str(e)}")
        return None, None

def handle_image_upload(uploaded_file):
    """Process uploaded image"""
    try:
        print(f"Processing uploaded file: {uploaded_file.name}, size: {uploaded_file.size} bytes")
        
        # Read image data
        img_data = uploaded_file.read()
        img = Image.open(io.BytesIO(img_data))
        print(f"Image opened successfully: size={img.size}, mode={img.mode}")
        
        # Save original
        st.session_state.last_drawing = img.copy()
        
        # Show original
        st.write("Original image:")
        st.image(img, caption="Original", width=200)
        
        # Preprocess
        print("Starting preprocessing")
        img = preprocess_image(img)
        
        # Show preprocessed
        st.write("Preprocessed image:")
        st.image(img, caption="Preprocessed", width=200)
        
        # Run OCR
        print("Running OCR")
        transcription = process_image_with_ocr(img_data)
        print(f"OCR output: {transcription}")
        
        # Clean up transcription
        transcription = transcription.strip()
        if not transcription:
            print("No text detected in image")
            return None, None, "Error", "No character detected in image. Please try again with a clearer image."
            
        st.write("### OCR Result")
        st.info(f"Detected text: {transcription}")
        
        # Grade attempt and submit review
        grade, feedback = grade_attempt(
            st.session_state.current_word,  # Pass the entire word object
            transcription
        )
        
        return transcription, transcription, grade, feedback
        
    except Exception as e:
        error_msg = f"Error processing image: {str(e)}"
        print(error_msg)
        print(f"Error type: {type(e)}")
        import traceback
        print("Traceback:", traceback.format_exc())
        st.error(error_msg)
        return None, None, "Error", "There was an error processing your image. Please try uploading a different image."

def get_next_word():
    """Get the next word, randomly selected"""
    if not st.session_state.words:
        logging.error("No words available in session state")
        return None
        
    # Get all words except the current one and previously seen words
    if 'seen_words' not in st.session_state:
        st.session_state.seen_words = set()
    
    # Make a copy of words to avoid modifying the original
    available_words = [w for w in st.session_state.words.copy() 
                      if w != st.session_state.current_word and 
                      w['id'] not in st.session_state.seen_words]
    
    logging.info(f"Available words: {len(available_words)} out of {len(st.session_state.words)}")
    logging.info(f"Seen words: {st.session_state.seen_words}")
    
    if not available_words:
        # If we've used all words, reset and shuffle
        logging.info("No more available words, resetting and shuffling")
        st.session_state.seen_words.clear()
        available_words = st.session_state.words.copy()
        random.shuffle(available_words)
        
    # Pick a random word from available ones
    next_word = random.choice(available_words)
    st.session_state.seen_words.add(next_word['id'])
    logging.info(f"Selected next word: {next_word}")
    return next_word.copy()  # Return a copy to avoid modifying the original

def practice_page():
    """Display practice state UI"""
    # First check if we have a valid group ID and words
    if not st.session_state.group_id or not st.session_state.words:
        st.error("No group selected or no words loaded. Please access this app through the main portal.")
        if st.button("Return to Setup"):
            st.session_state.state = SETUP
            st.rerun()
        return
    
    logging.info(f"Practice page - Session state: {st.session_state}")
    st.title("Japanese Writing Practice")
    st.info(f"Group ID: {st.session_state.group_id}")
    
    # Ensure we have current word
    if not st.session_state.current_word:
        st.session_state.current_word = get_next_word()
        st.rerun()
    
    # Debug info at the top for development
    with st.expander("Debug Info"):
        debug_info = {
            "state": st.session_state.state,
            "group_id": st.session_state.group_id,
            "session_id": st.session_state.session_id,
            "word_index": st.session_state.word_index,
            "current_word": st.session_state.current_word,
            "total_words": len(st.session_state.words),
            "seen_words": list(st.session_state.seen_words) if 'seen_words' in st.session_state else [],
            "reviews": st.session_state.reviews if 'reviews' in st.session_state else []
        }
        st.json(debug_info)
    
    # Display current word
    st.header("Current Word")
    st.markdown(f"""
    **Kanji:** {st.session_state.current_word['kanji']}
    
    **Reading:** {st.session_state.current_word['romaji']}
    
    **Meaning:** {st.session_state.current_word['english']}
    
    **Progress:** {len(st.session_state.seen_words) if 'seen_words' in st.session_state else 1} of {len(st.session_state.words)} words seen
    """)
    
    # Next word and shuffle buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Next Word"):
            # Get next random word
            next_word = get_next_word()
            if next_word:
                st.session_state.word_index = (st.session_state.word_index + 1) % len(st.session_state.words)
                st.session_state.current_word = next_word
                st.rerun()
            else:
                st.error("Failed to get next word")
    
    with col2:
        if st.button("Shuffle All Words"):
            # Clear seen words and get a new random word
            if 'seen_words' in st.session_state:
                st.session_state.seen_words.clear()
            random.shuffle(st.session_state.words)
            st.session_state.current_word = get_next_word()
            st.rerun()
    
    # Image upload section
    st.header("Practice Writing")
    st.markdown("""
    - Upload an image of the Japanese character
    - The image should contain a single character
    - Image should be clear and readable
    - Supported formats: PNG, JPG, JPEG
    """)
    
    image_file = st.file_uploader("Upload character image", type=['png', 'jpg', 'jpeg'])
    submit = st.button("Submit")
    
    if submit and image_file:
        result, img_array, status, feedback = handle_image_upload(image_file)
        if status == "Success":
            st.success(feedback)
            # Show next word button
            if st.button("Continue to Next Word"):
                next_word = get_next_word()
                if next_word:
                    st.session_state.current_word = next_word
                    st.rerun()
        elif status == "Error":
            st.error(feedback)
        elif status == "Warning":
            st.warning(feedback)

def setup_page():
    """Display setup state UI"""
    st.title("Japanese Writing Practice")
    
    # Get group ID from URL or use default
    group_id = st.query_params.get('group_id', '1')  # Default to group 1
    
    # Create a new study session
    try:
        response = requests.post(
            "http://localhost:5000/api/study-sessions",
            json={
                "group_id": int(group_id),
                "activity_id": 2  # 2 is Writing Practice
            }
        )
        if response.ok:
            data = response.json()
            st.session_state.session_id = data['session_id']
            print(f"Created new study session: {st.session_state.session_id}")
            print(f"View your reviews at: http://localhost:5173/sessions/")
        else:
            logging.error(f"Failed to create study session: {response.text}")
            st.error("Failed to create study session")
            return
    except Exception as e:
        logging.error(f"Error creating study session: {str(e)}")
        st.error("Error creating study session")
        return
    
    # Store group ID
    st.session_state.group_id = group_id
    
    # Fetch words for group
    words = fetch_words(group_id)
    if words:
        # Store words in session state
        st.session_state.words = words
        st.session_state.word_index = 0
        st.session_state.seen_words = set()  # Track which words we've seen
        st.session_state.state = PRACTICE
        st.rerun()
    else:
        st.error("Failed to fetch words for group")
        return

def validate_group(group_id):
    """Validate group ID exists in backend"""
    try:
        url = f"http://localhost:5000/groups/{group_id}"
        logging.info(f"Validating group ID at: {url}")
        response = requests.get(url)
        if response.ok:
            group_data = response.json()
            logging.info(f"Found group: {group_data}")
            return True
        else:
            logging.error(f"Group not found. Status: {response.status_code}")
            return False
    except Exception as e:
        logging.error(f"Error validating group: {str(e)}")
        return False

def init_session_state():
    """Initialize session state variables"""
    if 'state' not in st.session_state:
        st.session_state.state = SETUP
    if 'group_id' not in st.session_state:
        st.session_state.group_id = None
    if 'session_id' not in st.session_state:
        st.session_state.session_id = None
    if 'words' not in st.session_state:
        st.session_state.words = []
    if 'word_index' not in st.session_state:
        st.session_state.word_index = 0
    if 'current_word' not in st.session_state:
        st.session_state.current_word = None
    if 'seen_words' not in st.session_state:
        st.session_state.seen_words = set()
    if 'reviews' not in st.session_state:
        st.session_state.reviews = []

def main():
    """Main app entry point"""
    
    # Initialize session state
    init_session_state()
    
    # Display appropriate page based on state
    if st.session_state.state == SETUP:
        setup_page()
    elif st.session_state.state == PRACTICE:
        practice_page()

if __name__ == "__main__":
    main()