from typing import List, Dict
import json
import os
from ollama import Client

def extract_vocabulary(text: str, language: str = "Japanese") -> List[Dict]:
    """
    Extract vocabulary items from text using Ollama
    
    Args:
        text (str): Text to analyze
        language (str): Language of the text (default: Japanese)
        
    Returns:
        List[Dict]: List of vocabulary items with kanji, romaji, english meaning, and parts breakdown
    """
    try:
        client = Client()
        
        # Load prompt template
        prompt_path = os.path.join('Prompts', 'extract_vocabulary_prompt.md')
        with open(prompt_path, 'r', encoding='utf-8') as f:
            prompt_template = f.read()
        
        # Format prompt with text and language
        prompt = prompt_template.format(text=text, language=language)
        
        # Use the correct Ollama API format
        response = client.generate(
            model="mistral",
            prompt=prompt,
            stream=False
        )
        
        # Extract JSON from response
        response_text = response['response']
        start_idx = response_text.find('[')
        end_idx = response_text.rfind(']') + 1
        
        if start_idx == -1 or end_idx == 0:
            raise ValueError("No JSON array found in response")
            
        json_str = response_text[start_idx:end_idx]
        
        try:
            vocabulary = json.loads(json_str)
            if not isinstance(vocabulary, list):
                raise ValueError("Response is not a JSON array")
            return vocabulary
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")
        
    except Exception as e:
        print(f"[extract_vocabulary] Error: {str(e)}")
        print(f"[extract_vocabulary] Text sample: {text[:100]}...")
        return [{
            'error': str(e),
            'text': text[:100] + '...' if len(text) > 100 else text
        }]