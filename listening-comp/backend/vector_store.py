import boto3
import chromadb
import json
import os
from typing import List, Dict

class JLPTQuestionVectorStore:
    def __init__(self):
        """
        Initialize the vector store for JLPT listening test questions
        """
        # Always use backend/vector_storage
        current_dir = os.path.dirname(os.path.abspath(__file__))
        storage_path = os.path.join(current_dir, 'vector_storage')
        
        # Initialize Bedrock client for embeddings
        self.bedrock = boto3.client(
            service_name='bedrock-runtime',
            region_name='us-east-1'
        )
        
        # Initialize ChromaDB client
        self.chroma_client = chromadb.PersistentClient(path=storage_path)
        
        # Define collection names for each section
        self.section_collections = {
            1: "jlpt_section1_questions",
            2: "jlpt_section2_questions",
            3: "jlpt_section3_questions"
        }
    
    def _generate_embedding(self, text: str, model_id: str = 'amazon.titan-embed-text-v1') -> List[float]:
        """
        Generate embedding using Amazon Bedrock Titan
        
        Args:
            text (str): Text to embed
            model_id (str): Embedding model ID
        
        Returns:
            List[float]: Vector embedding
        """
        request_body = json.dumps({"inputText": text})
        
        response = self.bedrock.invoke_model(
            modelId=model_id,
            body=request_body
        )
        
        response_body = json.loads(response['body'].read())
        return response_body.get('embedding', [])
    
    def store_questions(self, questions: List[Dict], section: int):
        """
        Store questions in a section-specific collection
        
        Args:
            questions (List[Dict]): List of questions to store
            section (int): Section number (1, 2, or 3)
        """
        # Validate section
        if section not in self.section_collections:
            raise ValueError(f"Invalid section. Must be one of {list(self.section_collections.keys())}")
        
        # Get or create collection for the section
        collection = self.chroma_client.get_or_create_collection(
            name=self.section_collections[section]
        )
        
        # Process and store questions
        for i, question in enumerate(questions):
            # Convert question to a single string for embedding
            embedding_text = (
                f"Introduction: {question.get('introduction', '')} "
                f"Conversation: {question.get('conversation', '')} "
                f"Question: {question.get('question', '')}"
            )
            
            # Generate embedding
            embedding = self._generate_embedding(embedding_text)
            
            # Store question with full metadata
            collection.add(
                ids=[f"section{section}_question_{i}"],
                embeddings=[embedding],
                metadatas=[{
                    "full_question": json.dumps(question),
                    "section": section,
                    "introduction": question.get('introduction', ''),
                    "conversation": question.get('conversation', ''),
                    "question_text": question.get('question', '')
                }]
            )
    
    def query_similar_questions(
        self, 
        query_text: str, 
        section: int = None, 
        n_results: int = 5
    ) -> List[Dict]:
        """
        Find similar questions across sections or within a specific section
        
        Args:
            query_text (str): Text to find similar questions
            section (int, optional): Specific section to search
            n_results (int): Number of similar questions to return
        
        Returns:
            List[Dict]: Similar questions with metadata and distances
        """
        # Generate embedding for query
        query_embedding = self._generate_embedding(query_text)
        
        # Determine which collections to search
        search_collections = (
            [self.section_collections[section]] 
            if section and section in self.section_collections 
            else list(self.section_collections.values())
        )
        
        # Collect results from all specified collections
        all_results = []
        for collection_name in search_collections:
            collection = self.chroma_client.get_collection(name=collection_name)
            
            # Perform similarity search
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            # Process results
            for i in range(len(results['ids'][0])):
                # Get the full question from metadata without double-encoding
                metadata = results['metadatas'][0][i]
                question = metadata['full_question']
                if isinstance(question, str):
                    question = json.loads(question)
                
                all_results.append({
                    'id': results['ids'][0][i],
                    'metadata': question,  # Use the parsed question directly
                    'distance': results['distances'][0][i],
                    'section': metadata['section']
                })
        
        # Sort results by distance and return top n_results
        return sorted(all_results, key=lambda x: x['distance'])[:n_results]
    
    def generate_question_derivative(
        self, 
        original_question: Dict, 
        model_id: str = 'amazon.nova-micro-v1:0'
    ) -> Dict:
        """
        Generate a derivative question using Amazon Bedrock
        
        Args:
            original_question (Dict): Original question to derive from
            model_id (str): Bedrock LLM model to use
        
        Returns:
            Dict: Derivative question with same structure
        """
        prompt = f"""
        Generate a new JLPT listening test question following these guidelines:
        - Maintain the same section structure
        - Keep similar complexity level
        - Use different vocabulary but similar grammatical patterns

        Original Question:
        Introduction: {original_question.get('introduction', '')}
        Conversation: {original_question.get('conversation', '')}
        Question: {original_question.get('question', '')}

        New Derivative Question:
        """
        
        # Invoke Bedrock model
        response = self.bedrock.invoke_model(
            modelId=model_id,
            body=json.dumps({
                "prompt": prompt,
                "max_tokens_to_sample": 500,
                "temperature": 0.7,
                "top_p": 0.9
            })
        )
        
        # Process response
        response_body = json.loads(response['body'].read())
        derivative_text = response_body.get('completion', '')
        
        # Parse derivative question (you might need to adjust parsing)
        derivative_parts = derivative_text.split('\n')
        return {
            'introduction': derivative_parts[0].replace('Introduction: ', '').strip(),
            'conversation': derivative_parts[1].replace('Conversation: ', '').strip(),
            'question': derivative_parts[2].replace('Question: ', '').strip()
        }

# Example usage
if __name__ == "__main__":
    # Initialize the vector store
    vector_store = JLPTQuestionVectorStore()
    
    # Example of storing questions
    sample_questions_section1 = [
        {
            'introduction': '例朝学校で先生に会いました何と言いますか',
            'conversation': 'どうぞ入ってください、どうぞ来てください、どうぞ行ってください',
            'question': '何と言いますか'
        }
        # Add more questions...
    ]
    
    # Store questions for section 1
    vector_store.store_questions(sample_questions_section1, section=1)
    
    # Query similar questions
    query_text = "学校で先生に挨拶する場面"
    similar_questions = vector_store.query_similar_questions(query_text, section=1)
    
    # Print similar questions
    print("Similar Questions:")
    for q in similar_questions:
        print(f"Distance: {q['distance']}")
        print(f"Question: {q['metadata']}")
        print("---")