import streamlit as st
import sys
import os
from datetime import datetime

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from backend.question_generator import QuestionGenerator
from backend.chat import BedrockChat
from backend.get_transcript import YouTubeTranscriptDownloader
from backend.audio_generator import AudioGenerator

from typing import Dict
import json
from collections import Counter
import re

# Page config
st.set_page_config(
    page_title="JLPT Listening Practice",
    page_icon="🎧",
    layout="wide"
)

# Initialize session state
if 'transcript' not in st.session_state:
    st.session_state.transcript = None
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'question_generator' not in st.session_state:
    st.session_state.question_generator = QuestionGenerator()
if 'current_question' not in st.session_state:
    st.session_state.current_question = None
if 'correct_answer' not in st.session_state:
    st.session_state.correct_answer = None
if 'stage' not in st.session_state:
    st.session_state.stage = None
if 'audio_generator' not in st.session_state:
    st.session_state.audio_generator = AudioGenerator()
if 'current_audio_file' not in st.session_state:
    st.session_state.current_audio_file = None

def render_header():
    """Render the header section"""
    st.title("🎧 JLPT Listening Practice")
    st.markdown("""
    Transform YouTube transcripts into interactive Japanese learning experiences.
    
    This tool demonstrates:
    - Base LLM Capabilities
    - RAG (Retrieval Augmented Generation)
    - Amazon Bedrock Integration
    - Agent-based Learning Systems
    """)

def render_sidebar():
    """Render the sidebar with component selection"""
    with st.sidebar:
        st.header("Development Stages")
        
        # Main component selection
        selected_stage = st.radio(
            "Select Stage:",
            [
                "1. Chat with Nova",
                "2. Raw Transcript",
                "3. Structured Data",
                "4. RAG Implementation",
                "5. Interactive Learning"
            ]
        )
        
        # Stage descriptions
        stage_info = {
            "1. Chat with Nova": """
            **Current Focus:**
            - Basic Japanese learning
            - Understanding LLM capabilities
            - Identifying limitations
            """,
            
            "2. Raw Transcript": """
            **Current Focus:**
            - YouTube transcript download
            - Raw text visualization
            - Initial data examination
            """,
            
            "3. Structured Data": """
            **Current Focus:**
            - Text cleaning
            - Dialogue extraction
            - Data structuring
            """,
            
            "4. RAG Implementation": """
            **Current Focus:**
            - Bedrock embeddings
            - Vector storage
            - Context retrieval
            """,
            
            "5. Interactive Learning": """
            **Current Focus:**
            - Scenario generation
            - Audio synthesis
            - Interactive practice
            """
        }
        
        st.markdown("---")
        st.markdown(stage_info[selected_stage])
        
        return selected_stage

def render_chat_stage():
    """Render an improved chat interface"""
    st.header("Chat with Nova")

    # Initialize BedrockChat instance if not in session state
    if 'bedrock_chat' not in st.session_state:
        st.session_state.bedrock_chat = BedrockChat()

    # Introduction text
    st.markdown("""
    Start by exploring Nova's base Japanese language capabilities. Try asking questions about Japanese grammar, 
    vocabulary, or cultural aspects.
    """)

    # Initialize chat history if not exists
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="🧑‍💻" if message["role"] == "user" else "🤖"):
            st.markdown(message["content"])

    # Chat input area
    if prompt := st.chat_input("Ask about Japanese language...", key="chat_input"):
        # Process the user input
        process_message(prompt)

    # Example questions in sidebar
    with st.sidebar:
        st.markdown("### Try These Examples")
        example_questions = [
            "How do I say 'Where is the train station?' in Japanese?",
            "Explain the difference between は and が",
            "What's the polite form of 食べる?",
            "How do I count objects in Japanese?",
            "What's the difference between こんにちは and こんばんは?",
            "How do I ask for directions politely?"
        ]
        
        for q in example_questions:
            if st.button(q, use_container_width=True, type="secondary", key=q):
                # Process the example question
                process_message(q)
                st.rerun()

    # Add a clear chat button
    if st.session_state.messages:
        if st.button("Clear Chat", type="primary", key="clear_chat"):
            st.session_state.messages = []
            st.rerun()

def process_message(message: str):
    """Process a message and generate a response"""
    # Add user message to state and display
    st.session_state.messages.append({"role": "user", "content": message})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(message)

    # Generate and display assistant's response
    with st.chat_message("assistant", avatar="🤖"):
        response = st.session_state.bedrock_chat.generate_response(message)
        if response:
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

def count_characters(text):
    """Count Japanese and total characters in text"""
    if not text:
        return 0, 0
        
    def is_japanese(char):
        return any([
            '\u4e00' <= char <= '\u9fff',  # Kanji
            '\u3040' <= char <= '\u309f',  # Hiragana
            '\u30a0' <= char <= '\u30ff',  # Katakana
        ])
    
    jp_chars = sum(1 for char in text if is_japanese(char))
    return jp_chars, len(text)

def render_transcript_stage():
    """Render the raw transcript stage"""
    st.header("Raw Transcript Processing")
    
    # URL input
    url = st.text_input(
        "YouTube URL",
        placeholder="Enter a Japanese lesson YouTube URL",
        key="youtube_url"
    )
    
    # Download button and processing
    if url:
        if st.button("Download Transcript", key="download_transcript"):
            try:
                downloader = YouTubeTranscriptDownloader()
                transcript = downloader.get_transcript(url)
                if transcript:
                    # Extract video ID
                    video_id = downloader.extract_video_id(url)
                    
                    # Save transcript to file
                    if downloader.save_transcript(transcript, video_id):
                        st.success(f"Transcript saved to transcripts/{video_id}.txt")
                    else:
                        st.warning("Transcript downloaded but couldn't be saved to file.")
                    
                    # Store the raw transcript text in session state
                    transcript_text = "\n".join([entry['text'] for entry in transcript])
                    st.session_state.transcript = transcript_text
                    st.success("Transcript downloaded successfully!")
                else:
                    st.error("No transcript found for this video.")
            except Exception as e:
                st.error(f"Error downloading transcript: {str(e)}")

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Raw Transcript")
        if st.session_state.transcript:
            st.text_area(
                label="Raw text",
                value=st.session_state.transcript,
                height=400,
                disabled=True,
                key="raw_transcript"
            )
    
        else:
            st.info("No transcript loaded yet")
    
    with col2:
        st.subheader("Transcript Stats")
        if st.session_state.transcript:
            # Calculate stats
            jp_chars, total_chars = count_characters(st.session_state.transcript)
            total_lines = len(st.session_state.transcript.split('\n'))
            
            # Display stats
            st.metric("Total Characters", total_chars, key="total_chars")
            st.metric("Japanese Characters", jp_chars, key="jp_chars")
            st.metric("Total Lines", total_lines, key="total_lines")
        else:
            st.info("Load a transcript to see statistics")

def render_structured_stage():
    """Render the structured data stage"""
    st.header("Structured Data Processing")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Dialogue Extraction")
        # Placeholder for dialogue processing
        st.info("Dialogue extraction will be implemented here")
        
    with col2:
        st.subheader("Data Structure")
        # Placeholder for structured data view
        st.info("Structured data view will be implemented here")

def render_rag_stage():
    """Render the RAG implementation stage"""
    st.header("RAG System")
    
    # Query input
    query = st.text_input(
        "Test Query",
        placeholder="Enter a question about Japanese...",
        key="test_query"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Retrieved Context")
        # Placeholder for retrieved contexts
        st.info("Retrieved contexts will appear here")
        
    with col2:
        st.subheader("Generated Response")
        # Placeholder for LLM response
        st.info("Generated response will appear here")

def render_interactive_stage():
    """Render the interactive stage of the app"""
    st.title("JLPT Listening Practice")
    
    # Initialize session state
    if 'question_generator' not in st.session_state:
        st.session_state.question_generator = QuestionGenerator()
    if 'current_question' not in st.session_state:
        st.session_state.current_question = None
    if 'feedback' not in st.session_state:
        st.session_state.feedback = None
    if 'selected_answer' not in st.session_state:
        st.session_state.selected_answer = None
    if 'show_audio' not in st.session_state:
        st.session_state.show_audio = False
    
    # Add history to sidebar
    with st.sidebar:
        # Clear any existing content in sidebar
        st.empty()
        
        st.markdown("### Question History")
        
        # Get current section and topic
        section_num = st.session_state.get('section', 2)
        selected_topic = st.session_state.get('topic', None)
        
        # Add filter toggle
        show_all_history = st.checkbox("Show all questions", value=True)
        
        # Get question history
        history = st.session_state.question_generator.get_question_history(
            section=None if show_all_history else section_num,
            topic=None if show_all_history else selected_topic
        )
        
        if not history:
            st.info("No questions in history yet. Generate some questions to see them here!")
        else:
            # Show questions in reverse chronological order with custom styling
            st.markdown("""
            <style>
            .history-item {
                padding: 10px;
                margin: 6px 0;
                border-radius: 6px;
                border: 1px solid #e1e4e8;
                background-color: #ffffff;
                cursor: pointer;
                transition: all 0.2s;
            }
            .history-item:hover {
                background-color: #f6f8fa;
                border-color: #0366d6;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }
            .history-meta {
                color: #586069;
                font-size: 12px;
                margin-bottom: 4px;
            }
            .history-preview {
                font-size: 14px;
                color: #24292e;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Create a container for scrollable history
            with st.container():
                for entry in reversed(history):
                    timestamp = datetime.fromisoformat(entry["timestamp"]).strftime("%H:%M")
                    question = entry["question"]
                    preview = question.get("introduction", "")[:40] + "..."
                    
                    # Create a clickable item
                    if st.button(
                        f"""
                        Section {entry['section']} - {entry['topic']} ({timestamp})
                        {preview}
                        """,
                        key=f"load_q_{entry['id']}",
                        use_container_width=True
                    ):
                        st.session_state.current_question = question
                        st.session_state.feedback = None
                        st.session_state.section = entry['section']
                        st.session_state.topic = entry['topic']
                        st.rerun()
    
    # Section selection
    st.markdown("### Section Selection")
    section_num = st.radio(
        "Choose a section:",
        options=[2, 3],
        format_func=lambda x: f"Section {x}",
        horizontal=True,
        key="section"
    )
    
    # Topic selection based on section
    topics = {
        2: ["Daily Conversation", "Shopping", "Restaurant", "School Life", "Work Situation"],
        3: ["Public Announcement", "Train Station", "Hospital", "Office", "Event Information"]
    }
    
    selected_topic = st.selectbox(
        "Choose a topic:",
        options=topics.get(section_num, []),
        key="topic"
    )
    
    # Generate new question button
    if st.button("Generate New Question", key="generate_question"):
        try:
            new_question = st.session_state.question_generator.generate_question(
                section=section_num,
                topic=selected_topic
            )
            if new_question:
                # Remove any existing audio file reference
                new_question.pop('audio_file', None)
                st.session_state.current_question = new_question
                st.session_state.feedback = None
                st.session_state.show_audio = False
                st.rerun()
            else:
                st.error("Failed to generate a new question. Please try again.")
        except Exception as e:
            st.error(f"Error generating question: {str(e)}")

    # Display current question
    if st.session_state.current_question:
        question = st.session_state.current_question
        
        # Add Japanese font styling for generated content
        st.markdown("""
        <style>
        .japanese-text {
            font-family: "Noto Sans JP", "MS Gothic", sans-serif;
            font-size: 16px;
            line-height: 1.6;
        }
        .audio-controls {
            margin: 20px 0;
            padding: 20px;
            border-radius: 10px;
            background-color: #f0f7ff;
            border: 1px solid #cce5ff;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .audio-button {
            margin: 10px 0;
            padding: 10px 20px;
            border-radius: 5px;
            background-color: #0066cc;
            color: white;
            border: none;
            cursor: pointer;
            transition: all 0.2s;
        }
        .audio-button:hover {
            background-color: #0052a3;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Audio playback section
        with st.container():
            st.markdown('<div class="audio-controls">', unsafe_allow_html=True)
            st.markdown("### 🎧 Question Audio")
            
            if not st.session_state.show_audio:
                # Only show the generate button if audio hasn't been generated
                if st.button("🔊 Generate Audio", key="generate_audio", use_container_width=True):
                    with st.spinner("Generating audio..."):
                        audio_file = st.session_state.audio_generator.generate_audio(question)
                        if audio_file and os.path.exists(audio_file):
                            # Create a new copy of the question to avoid modifying the original
                            updated_question = question.copy()
                            updated_question['audio_file'] = audio_file
                            st.session_state.current_question = updated_question
                            st.session_state.show_audio = True
                            st.rerun()
                        else:
                            st.error("Failed to generate audio. Please try again.")
            else:
                # Show the audio player and a regenerate button
                if 'audio_file' in question and os.path.exists(question['audio_file']):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.audio(question['audio_file'])
                    with col2:
                        if st.button("🔄 Regenerate", key="regenerate_audio", use_container_width=True):
                            with st.spinner("Regenerating audio..."):
                                audio_file = st.session_state.audio_generator.generate_audio(question)
                                if audio_file and os.path.exists(audio_file):
                                    updated_question = question.copy()
                                    updated_question['audio_file'] = audio_file
                                    st.session_state.current_question = updated_question
                                    st.rerun()
                                else:
                                    st.error("Failed to regenerate audio. Please try again.")
                else:
                    st.error("Audio file not found. Please try regenerating the audio.")
                    if st.button("🔄 Try Again", key="retry_audio", use_container_width=True):
                        st.session_state.show_audio = False
                        st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Display based on section type
        if section_num == 2:
            st.subheader("Dialogue Question")
            with st.container():
                st.markdown("**Introduction:**")
                st.markdown(f'<div class="japanese-text">{question.get("introduction", "")}</div>', unsafe_allow_html=True)
                st.markdown("**Conversation:**")
                st.markdown(f'<div class="japanese-text">{question.get("conversation", "").replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
        else:
            st.subheader("Situational Question")
            with st.container():
                st.markdown("**Situation:**")
                st.markdown(f'<div class="japanese-text">{question.get("introduction", "")}</div>', unsafe_allow_html=True)
                st.markdown("**Announcement:**")
                st.markdown(f'<div class="japanese-text">{question.get("conversation", "").replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
        
        st.markdown("**Question:**")
        st.markdown(f'<div class="japanese-text">{question.get("question", "")}</div>', unsafe_allow_html=True)
        
        # Display options as radio buttons with Japanese text
        if 'options' in question:
            options = question['options']
            st.markdown("**Options:**")
            selected = st.radio(
                "Select your answer:",
                options=range(1, len(options) + 1),
                format_func=lambda x: f"{x}. {options[x-1]}",
                key="answer_radio"
            )
            st.session_state.selected_answer = selected
        else:
            st.text_area("Your answer:", key="text_answer")
            st.session_state.selected_answer = st.session_state.text_answer
        
        # Submit answer button
        if st.button("Submit Answer", key="submit_answer"):
            try:
                feedback = st.session_state.question_generator.provide_feedback(
                    question=st.session_state.current_question,
                    user_answer=str(st.session_state.selected_answer)
                )
                
                # Show feedback with correct answer highlighting
                st.session_state.feedback = feedback
                correct_answer = st.session_state.current_question.get('correct_answer', 0) + 1
                user_answer = st.session_state.selected_answer
                
                # Display feedback
                st.markdown("### Feedback")
                is_correct = user_answer == correct_answer
                st.markdown(f"Your answer: {'✅' if is_correct else '❌'} Option {user_answer}")
                st.markdown(f"Correct answer: Option {correct_answer}")
                
                # Display feedback message with appropriate styling
                if is_correct:
                    st.success("✨ Correct! Great job! ✨")
                else:
                    st.error("❌ Incorrect. Let's learn from this!")
                
                # Display the feedback text
                st.info(feedback)
                
            except Exception as e:
                st.error(f"Error providing feedback: {str(e)}")

def main():
    """Main entry point for the Streamlit app"""
    render_header()
    selected_stage = render_sidebar()
    
    # Render appropriate stage
    if selected_stage == "1. Chat with Nova":
        render_chat_stage()
    elif selected_stage == "2. Raw Transcript":
        render_transcript_stage()
    elif selected_stage == "3. Structured Data":
        render_structured_stage()
    elif selected_stage == "4. RAG Implementation":
        render_rag_stage()
    elif selected_stage == "5. Interactive Learning":
        # Hide the development UI for interactive learning
        st.markdown("""
        <style>
        /* Hide the development header and description */
        section.main > div:first-child {display: none}
        /* Hide the development stages in sidebar */
        [data-testid="stSidebarNav"] {display: none}
        /* Hide development stages radio but keep the rest of sidebar */
        [data-testid="stSidebar"] .stRadio {display: none}
        [data-testid="stSidebar"] .stMarkdown:first-child {display: none}
        [data-testid="stSidebar"] hr {display: none}
        </style>
        """, unsafe_allow_html=True)
        render_interactive_stage()
        
        # Add a small reset button at the bottom
        if st.button("⬅️ Back to Development Stages", use_container_width=True):
            st.rerun()
    
    # Debug section at the bottom (only show if not in interactive learning)
    if selected_stage != "5. Interactive Learning":
        with st.expander("Debug Information"):
            st.json({
                "selected_stage": selected_stage,
                "transcript_loaded": st.session_state.transcript is not None,
                "chat_messages": len(st.session_state.messages)
            })

if __name__ == "__main__":
    main()