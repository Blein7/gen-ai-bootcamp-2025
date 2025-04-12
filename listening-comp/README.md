# JLPT Listening Practice Application

An interactive application for practicing Japanese language listening comprehension based on JLPT exam format. This application uses AWS Bedrock for natural language processing and Amazon Polly for text-to-speech capabilities.

## Features

- **Chat with Nova**: Practice basic Japanese concepts through conversational AI
- **Transcript Processing**: Download and process YouTube Japanese transcripts
- **Structured Data**: Convert raw transcripts into structured JLPT-style questions
- **RAG Implementation**: Utilize Retrieval Augmented Generation for context-aware responses
- **Interactive Learning**: Generate audio and practice with JLPT-style listening exercises

## Requirements

- Docker and Docker Compose
- AWS account with access to Bedrock and Polly services
- AWS credentials with appropriate permissions

## Setup and Installation

### Using Docker (Recommended)

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd gen-ai-bootcamp-2025
   ```

2. **Configure AWS credentials**:
   Create a `.env` file in the project root with your AWS credentials:
   ```
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_DEFAULT_REGION=us-east-1
   ```

3. **Run with Docker Compose**:
   ```bash
   docker-compose up -d listening-comp chroma-db
   ```

4. **Access the application**:
   Open your browser and navigate to http://localhost:8501

### Manual Installation (Alternative)

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd gen-ai-bootcamp-2025/listening-comp
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install ffmpeg**:
   - On Ubuntu/Debian: `sudo apt-get install ffmpeg`
   - On Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH

4. **Configure AWS credentials**:
   ```bash
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   export AWS_DEFAULT_REGION=us-east-1
   ```

5. **Run the application**:
   ```bash
   streamlit run frontend/main.py
   ```

## Project Structure

- `frontend/`: Streamlit interface code
- `backend/`: Core functionality and services
  - `vector_store.py`: Manages vector embeddings for RAG
  - `question_generator.py`: Generates JLPT-style questions
  - `audio_generator.py`: Creates audio files for listening practice
  - `structured_data.py`: Processes and structures transcript data
- `data/`: Contains transcript and question data
  - `transcripts/`: Raw transcript files
  - `questions/`: Generated structured questions

## Usage Guide

1. **Start with Chat**: Begin by exploring Nova's Japanese language capabilities
2. **Process Transcripts**: Download and visualize YouTube Japanese content
3. **Generate Questions**: Create structured JLPT-style listening questions
4. **Practice Listening**: Generate audio and test your comprehension skills

## Troubleshooting

- **AWS Credential Issues**: Ensure your AWS credentials have access to Bedrock and Polly services
- **Audio Generation Problems**: Verify ffmpeg is properly installed
- **ChromaDB Connection**: Make sure the ChromaDB service is running and accessible

## Dependencies

This project relies on the following key libraries (specified in requirements.txt):
- boto3==1.37.33 - AWS SDK for Python
- streamlit==1.26.0 - Web application framework
- chromadb==1.0.4 - Vector database for RAG implementation
- python-dotenv==1.1.0 - Environment variable management
- langchain==0.0.300 - LLM framework
- ffmpeg-python==0.2.0 - Python bindings for FFmpeg

## License

[Specify the license under which this project is released]

## Acknowledgments

- AWS Bedrock for providing the LLM capabilities
- Amazon Polly for text-to-speech services
- ChromaDB for vector storage functionality