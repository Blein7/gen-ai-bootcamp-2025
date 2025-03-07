import boto3
import json
from typing import List, Dict, Tuple, Optional

# Import your existing VectorStore class
from .vector_store import JLPTQuestionVectorStore

class QuestionGenerator:
    def __init__(self):
        """
        Initialize Bedrock client and vector store
        """
        self.bedrock_client = boto3.client('bedrock-runtime', region_name="us-east-1")
        self.vector_store = JLPTQuestionVectorStore()
        self.model_id = "amazon.nova-micro-v1:0"

    def _invoke_bedrock(self, prompt: str) -> Optional[str]:
        """
        Invoke Bedrock with the given prompt
        """
        try:
            messages = [{
                "role": "user",
                "content": [{
                    "text": prompt
                }]
            }]
            
            response = self.bedrock_client.converse(
                modelId=self.model_id,
                messages=messages,
                inferenceConfig={"temperature": 0.7}
            )
            
            return response['output']['message']['content'][0]['text']
        except Exception as e:
            print(f"Error invoking Bedrock: {str(e)}")
            return None

    def generate_similar_question(self, query_text: str, section: int) -> Dict:
        """
        Generate a new question similar to existing ones using RAG
        
        Args:
            query_text (str): Query text to find similar questions
            section (int): JLPT section number (1, 2, or 3)
            
        Returns:
            Dict: New generated question with introduction, conversation, and question
        """
        # Get similar questions for context
        try:
            similar_questions = self.vector_store.query_similar_questions(query_text=query_text, section=section)
        except Exception as e:
            # If we still have issues (e.g., empty collection), return a default question
            print(f"Error querying similar questions: {e}")
            return self._generate_default_question(section)
        
        # If no similar questions found, create a default question
        if not similar_questions:
            return self._generate_default_question(section)
        
        # Extract the most similar questions for context
        context_questions = []
        for q in similar_questions[:3]:  # Use top 3 similar questions
            if 'metadata' in q and isinstance(q['metadata'], dict):
                context_questions.append(q['metadata'])
        
        # Format prompt for Nova
        prompt = self._format_generation_prompt(context_questions, query_text, section)
        
        # Generate new question using Bedrock
        generated_text = self._invoke_bedrock(prompt)
        if generated_text:
            return self._parse_generated_question(generated_text)
        else:
            return self._generate_default_question(section)
    
    def _format_generation_prompt(self, context_questions: List[Dict], query_text: str, section: int) -> str:
        """
        Format the prompt for generating a new question
        
        Args:
            context_questions (List[Dict]): List of similar questions for context
            query_text (str): The user's query text
            section (int): JLPT section number
            
        Returns:
            str: Formatted prompt for Bedrock
        """
        # Format context questions
        context_str = ""
        for i, q in enumerate(context_questions):
            context_str += f"Example {i+1}:\n"
            context_str += f"Introduction: {q.get('introduction', '')}\n"
            context_str += f"Conversation: {q.get('conversation', '')}\n"
            context_str += f"Question: {q.get('question', '')}\n\n"
        
        # Create full prompt
        prompt = f"""
You are a Japanese language tutor specializing in JLPT listening test questions.

Create a new JLPT Section {section} listening question that's similar to the examples but not identical.
Use the user's query theme: "{query_text}" to guide the creation.

Here are some example questions for reference:
{context_str}

Please create a new question with the following structure:
1. Introduction (in Japanese): A brief introduction to the listening scenario
2. Conversation (in Japanese): The conversation or statement to be heard
3. Question (in Japanese): The question asked about the conversation

Format your response in JSON format with three keys: introduction, conversation, and question.
"""
        return prompt
    
    def _parse_generated_question(self, generated_text: str) -> Dict:
        """
        Parse the generated text into a structured question
        
        Args:
            generated_text (str): Generated text from Bedrock
            
        Returns:
            Dict: Structured question
        """
        # Try to extract JSON if present
        try:
            # Look for JSON-like structure in the text
            start_idx = generated_text.find('{')
            end_idx = generated_text.rfind('}')
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = generated_text[start_idx:end_idx+1]
                question_dict = json.loads(json_str)
                
                # Ensure all required fields are present
                if all(k in question_dict for k in ['introduction', 'conversation', 'question']):
                    return question_dict
        except:
            pass
        
        # Fallback: Try to parse based on headers
        try:
            lines = generated_text.split('\n')
            introduction = ""
            conversation = ""
            question = ""
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if "introduction:" in line.lower():
                    current_section = "introduction"
                    introduction = line.split(":", 1)[1].strip()
                elif "conversation:" in line.lower():
                    current_section = "conversation"
                    conversation = line.split(":", 1)[1].strip()
                elif "question:" in line.lower():
                    current_section = "question"
                    question = line.split(":", 1)[1].strip()
                elif current_section:
                    # Append to current section
                    if current_section == "introduction":
                        introduction += " " + line
                    elif current_section == "conversation":
                        conversation += " " + line
                    elif current_section == "question":
                        question += " " + line
            
            return {
                "introduction": introduction.strip(),
                "conversation": conversation.strip(),
                "question": question.strip()
            }
        except:
            # If all parsing fails, return a simple structure
            return {
                "introduction": "自動生成された問題",
                "conversation": generated_text[:100],
                "question": "何について話していますか"
            }
    
    def _generate_default_question(self, section: int) -> Dict:
        """
        Generate a default question when RAG fails
        
        Args:
            section (int): JLPT section number
            
        Returns:
            Dict: Default question
        """
        if section == 1:
            return {
                "introduction": "朝学校で先生に会いました。何と言いますか。",
                "conversation": "おはようございます、こんにちは、さようなら",
                "question": "何と言いますか"
            }
        elif section == 2:
            return {
                "introduction": "友達と映画を見た後の会話です。",
                "conversation": "A: 映画はどうでしたか？\nB: とても面白かったです。特に最後のシーンが印象的でした。",
                "question": "Bさんはどう思いましたか？"
            }
        else:
            return {
                "introduction": "大学のレポートについての会話です。",
                "conversation": "A: レポートの締め切りはいつですか？\nB: 今週の金曜日です。でも、提出が遅れる場合は先生に相談してください。",
                "question": "レポートの締め切りはいつですか？"
            }
    
    def get_feedback(self, user_answer: str, correct_answer: str, question_text: str) -> Tuple[bool, str]:
        """
        Evaluate the user's answer and provide feedback
        
        Args:
            user_answer (str): The user's answer
            correct_answer (str): The correct answer
            question_text (str): The original question text
            
        Returns:
            Tuple[bool, str]: (is_correct, feedback_explanation)
        """
        prompt = f"""
You are a Japanese language tutor evaluating a student's answer to a JLPT listening question.

Question: {question_text}
Correct answer: {correct_answer}
Student's answer: {user_answer}

First determine if the student's answer is correct. Consider slight variations or synonyms as correct.
Then provide helpful feedback explaining why the answer is correct or incorrect in a supportive way.
If incorrect, explain the correct answer and what the student may have misunderstood.

Format your response exactly as follows:
CORRECT: Yes or No
EXPLANATION: Your detailed feedback here
"""
        
        try:
            response = self.bedrock_client.converse(
                modelId=self.model_id,
                messages=[{
                    "role": "user",
                    "content": [{
                        "text": prompt
                    }]
                }],
                inferenceConfig={"temperature": 0.2}
            )
            
            # Parse response
            feedback_text = response['output']['message']['content'][0]['text']
            
            # Extract correctness and explanation
            is_correct = False
            explanation = ""
            
            for line in feedback_text.split('\n'):
                if line.startswith("CORRECT:"):
                    is_correct = "yes" in line.lower()
                elif line.startswith("EXPLANATION:"):
                    explanation = line[len("EXPLANATION:"):].strip()
                    # Get the rest of the explanation if it continues
                    rest_idx = feedback_text.find("EXPLANATION:") + len("EXPLANATION:")
                    explanation = feedback_text[rest_idx:].strip()
            
            return is_correct, explanation
        
        except Exception as e:
            print(f"Error generating feedback: {e}")
            # Fallback simple evaluation
            is_correct = user_answer.lower() == correct_answer.lower()
            explanation = "正解です！" if is_correct else f"残念ながら不正解です。正解は「{correct_answer}」です。"
            return is_correct, explanation