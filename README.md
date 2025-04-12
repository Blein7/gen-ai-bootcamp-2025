# Generative AI Bootcamp 2025 - Language Learning Tools

This repository contains a collection of AI-powered language learning tools developed during the Generative AI Bootcamp 2025. Each tool focuses on different aspects of language learning, leveraging various AI technologies.

## Components

### 1. JLPT Listening Practice
An interactive application for practicing Japanese language listening comprehension based on JLPT exam format.

**Key Features:**
- Chat with Nova for Japanese language practice
- YouTube transcript processing
- JLPT-style question generation
- Interactive listening exercises with audio generation
- RAG implementation for context-aware responses

**Technologies:**
- AWS Bedrock, Amazon Polly
- ChromaDB for vector storage
- Streamlit for frontend

[Learn more about JLPT Listening Practice](./listening-comp/README.md)

### 2. Song Vocabulary
A tool that helps language learners discover and learn vocabulary through music.

**Key Features:**
- Extract lyrics and identify useful vocabulary
- Generate example sentences
- Create vocabulary lists from music

**Technologies:**
- Ollama for local LLM deployment
- Song lyrics APIs

### 3. Writing Practice
A tool for improving writing skills in the target language.

**Key Features:**
- Writing prompts generation
- Feedback on grammar and vocabulary
- Progress tracking

**Technologies:**
- OpenAI API
- Writing assessment algorithms

### 4. Language Portal Backend
A centralized backend that manages user data, vocabulary lists, and progress tracking.

**Key Features:**
- User authentication
- Vocabulary storage
- Progress tracking
- API endpoints for frontend applications

**Technologies:**
- Flask
- SQLite database

## Running the Project

### Prerequisites
- Docker and Docker Compose
- AWS account with Bedrock and Polly access
- OpenAI API key (for Writing Practice)

### Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd gen-ai-bootcamp-2025
   ```

2. **Configure environment variables**:
   Create a `.env` file in the project root:
   ```
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_DEFAULT_REGION=us-east-1
   OPENAI_API_KEY=your_openai_api_key
   ```

3. **Start services with Docker Compose**:
   ```bash
   # Start all services
   docker-compose up -d
   
   # Or start specific services
   docker-compose up -d listening-comp chroma-db
   ```

4. **Access the applications**:
   - JLPT Listening Practice: http://localhost:8501
   - Song Vocabulary: http://localhost:8004
   - Writing Practice: http://localhost:8503
   - Language Portal Frontend: http://localhost:3000

## Project Structure

```
gen-ai-bootcamp-2025/
├── listening-comp/    # JLPT Listening Practice application
├── song-vocab/        # Song Vocabulary application
├── writing-practice/  # Writing Practice application
├── lang-portal/       # Language Portal components
│   ├── backend-flask/ # Backend Flask API
│   └── frontend-react/ # Frontend React application
└── docker-compose.yml # Docker services configuration
```

## Contributing

[Provide contribution guidelines if applicable]

## License

[Specify the license under which this project is released]

## Acknowledgments

- AWS for providing Bedrock and other cloud services
- OpenAI for API access
- All contributors to the Generative AI Bootcamp 2025