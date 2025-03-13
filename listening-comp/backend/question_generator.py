import boto3
import json
from typing import Dict, List, Optional
from datetime import datetime
from backend.vector_store import JLPTQuestionVectorStore
from backend.question_history import QuestionHistory

# Model ID for question generation
MODEL_ID = "amazon.nova-micro-v1:0"

class QuestionGenerator:
    def __init__(self):
        """Initialize vector store and Bedrock client for RAG-based question generation"""
        self.vector_store = JLPTQuestionVectorStore()
        self.bedrock_client = boto3.client('bedrock-runtime', region_name="us-east-1")
        self.history = QuestionHistory()
    
    def generate_question(self, section: int = None, topic: str = None) -> Optional[Dict]:
        """Generate a new question using RAG workflow"""
        try:
            # 1. Find similar questions using semantic search with topic context
            query = f"Generate a new JLPT listening question about {topic}" if topic else "Generate a new JLPT listening question"
            similar_questions = self.vector_store.query_similar_questions(
                query_text=query,
                section=section,
                n_results=2
            )
            
            if not similar_questions:
                print("No similar questions found in vector store")
                return None
            
            # 2. Use retrieved questions as context for generation
            question_context = similar_questions[0]['metadata']  # Already parsed by vector store
            
            # 3. Generate new question using converse API with topic guidance
            messages = [{
                "role": "user",
                "content": [{
                    "text": self._create_question_prompt(question_context, topic)
                }]
            }]
            
            response = self.bedrock_client.converse(
                modelId=MODEL_ID,
                messages=messages,
                inferenceConfig={
                    "temperature": 0.7,
                    "topP": 0.9,
                    "maxTokens": 500
                }
            )
            
            # 4. Parse response into question format
            new_question = self._parse_question_response(response['output']['message']['content'][0]['text'])
            
            # 5. Add topic and timestamp to the question metadata
            if new_question:
                new_question['topic'] = topic
                new_question['timestamp'] = datetime.now().isoformat()
            
            # 6. Store the new question in vector store and history
            if new_question and section:
                self.vector_store.store_questions([new_question], section)
                # Store in history with section and topic
                self.history.add_question(new_question, section, topic or "General")
            
            return new_question
            
        except Exception as e:
            print(f"Error generating question: {str(e)}")
            return None
    
    def provide_feedback(self, question: Dict, user_answer: str) -> str:
        """Provide contextual feedback using RAG workflow"""
        try:
            # 1. Find similar questions for context
            similar_questions = self.vector_store.query_similar_questions(
                query_text=f"{question.get('introduction', '')} {question.get('conversation', '')}",
                section=None,
                n_results=2
            )
            
            # 2. Generate feedback using converse API
            messages = [{
                "role": "user",
                "content": [{
                    "text": self._create_feedback_prompt(question, [q['metadata'] for q in similar_questions], user_answer)
                }]
            }]
            
            response = self.bedrock_client.converse(
                modelId=MODEL_ID,
                messages=messages,
                inferenceConfig={
                    "temperature": 0.7,
                    "topP": 0.9,
                    "maxTokens": 500
                }
            )
            
            return response['output']['message']['content'][0]['text']
            
        except Exception as e:
            print(f"Error providing feedback: {str(e)}")
            return "Unable to generate feedback at this time."
    
    def get_question_history(self, section: Optional[int] = None, topic: Optional[str] = None) -> List[Dict]:
        """Get questions from history with optional filters"""
        return self.history.get_questions(section, topic)
    
    def get_question_by_id(self, question_id: int) -> Optional[Dict]:
        """Get a specific question by ID"""
        return self.history.get_question_by_id(question_id)
    
    def _create_question_prompt(self, context: Dict, topic: str = None) -> str:
        """Create prompt for generating a new question"""
        # Topic-specific guidance for options
        topic_guidance = {
            "Daily Conversation": "Focus on different responses, reactions, or solutions to daily situations",
            "Shopping": "Include options about product choices, prices, preferences, or shopping decisions",
            "Restaurant": "Vary between menu items, dining preferences, reservations, or special requests",
            "School Life": "Include options about study plans, club activities, assignments, or school events",
            "Work Situation": "Focus on workplace decisions, meeting schedules, project details, or business interactions",
            "Public Announcement": "Include options about event details, schedule changes, locations, or important notices",
            "Train Station": "Vary between platform numbers, train lines, destinations, or service announcements",
            "Hospital": "Include options about appointments, departments, medical procedures, or visiting hours",
            "Office": "Focus on meeting rooms, document handling, office procedures, or work schedules",
            "Event Information": "Include options about event times, locations, requirements, or program details"
        }
        
        option_guidance = topic_guidance.get(topic, "Ensure options are diverse and contextually relevant")
        
        return f"""
You are a JLPT listening test question creator. Generate a new question following these requirements:

Topic: {topic if topic else 'General JLPT listening practice'}

Original Question for Reference:
Introduction: {context.get('introduction', '')}
Conversation: {context.get('conversation', '')}
Question: {context.get('question', '')}
Options: {', '.join(context.get('options', []))}

Requirements for the new question:
1. Introduction (状況説明) must be in Japanese, describing a {topic} situation naturally
2. Conversation must be in Japanese, using appropriate keigo and natural dialogue
3. Question (質問) must be in Japanese
4. Options must be in Japanese, with 4 plausible but distinct choices
5. Correct answer should be indicated as a number (0-3, where 0 is the first option)

Important:
- {option_guidance}
- Avoid making all options about time durations
- Each option should present a different scenario or choice
- Options should be realistic and contextually appropriate

Format the response exactly as follows:
{{
    "introduction": "(Japanese introduction text)",
    "conversation": "(Japanese dialogue)",
    "question": "(Japanese question text)",
    "options": ["(Japanese option 1)", "(Japanese option 2)", "(Japanese option 3)", "(Japanese option 4)"],
    "correct_answer": (0-3)
}}

Note: The conversation should maintain JLPT level appropriateness and test listening comprehension skills.
"""
    
    def _parse_question_response(self, response_text: str) -> Optional[Dict]:
        """Parse the response from the model into a question format"""
        try:
            # Find the JSON block in the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx == -1 or end_idx == 0:
                print("No JSON found in response")
                return None
            
            json_str = response_text[start_idx:end_idx]
            question = json.loads(json_str)
            
            # Validate required fields
            required_fields = ['introduction', 'conversation', 'question', 'options', 'correct_answer']
            if not all(field in question for field in required_fields):
                print("Missing required fields in question")
                return None
            
            # Ensure correct_answer is an integer
            question['correct_answer'] = int(question['correct_answer'])
            
            return question
        except Exception as e:
            print(f"Error parsing question response: {str(e)}")
            return None
    
    def _create_feedback_prompt(self, question: Dict, similar_questions: List[Dict], user_answer: str) -> str:
        """Create prompt for generating feedback"""
        # Get the correct and selected options
        correct_option = question.get('options', [])[question.get('correct_answer', 0)]
        user_option = question.get('options', [])[int(user_answer)-1] if question.get('options') else user_answer
        
        return f"""
You are a JLPT listening test evaluator. Analyze this response and provide helpful feedback:

Question Details:
- Introduction: {question.get('introduction', '')}
- Conversation: {question.get('conversation', '')}
- Question: {question.get('question', '')}
- Student's Answer: {user_option}
- Correct Answer: {correct_option}

Similar Questions for Context:
{self._format_similar_questions(similar_questions)}

Provide feedback in this format:
1. Start with whether the answer is correct or incorrect
2. Explain the key points from the conversation that led to the correct answer
3. Highlight any important Japanese expressions or grammar patterns used
4. Give specific tips for improving listening comprehension
5. End with an encouraging note

Keep the feedback clear and concise in English to help the student understand and improve.
"""

    def _format_similar_questions(self, questions: List[Dict]) -> str:
        """Format similar questions for context"""
        result = []
        for i, q in enumerate(questions, 1):
            result.append(f"Similar Question {i}:")
            result.append(f"Introduction: {q.get('introduction', '')}")
            result.append(f"Conversation: {q.get('conversation', '')}")
            result.append(f"Question: {q.get('question', '')}\n")
        return "\n".join(result)