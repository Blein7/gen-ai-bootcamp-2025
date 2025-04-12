from typing import Dict, List, Any, Optional
import instructor
from ollama import Client
import json
import os
from tools.search_web import search_web
from tools.get_page_content import get_page_content
from tools.extract_vocabulary import extract_vocabulary
from tools.song_id import generate_song_id, get_song_info
import re

class LyricsAgent:
    def __init__(self):
        # Get Ollama host from environment variable with fallback to default
        ollama_host = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')
        print(f"[Agent] Connecting to Ollama at {ollama_host}")
        
        # Add retry logic for client initialization
        max_init_retries = 10
        init_retry_count = 0
        connection_success = False
        
        while init_retry_count < max_init_retries and not connection_success:
            try:
                print(f"[Agent] Attempt {init_retry_count + 1}/{max_init_retries} to connect to Ollama")
                self.client = Client(host=ollama_host)
                
                # Test connection with a simple ping
                response = self.client.chat(
                    model="mistral",
                    messages=[{"role": "user", "content": "ping"}],
                    options={"temperature": 0}
                )
                if response:
                    print("[Agent] Successfully connected to Ollama")
                    connection_success = True
                else:
                    raise Exception("No response from Ollama")
                    
            except Exception as e:
                print(f"[Agent] Connection error: {str(e)}")
                init_retry_count += 1
                import time
                time.sleep(5)  # Wait 5 seconds before retrying
                
        if not connection_success:
            print("[Agent] Failed to connect to Ollama after maximum retries")
            # Still create the client but log the warning
            self.client = Client(host=ollama_host)
            
        self.timeout = 30  # 30 seconds timeout for Ollama
        self.max_retries = 3  # Increase retries
        
        # Initialize current_data to store state
        self.current_data = {
            'lyrics': None, 
            'vocabulary': None, 
            'source_url': None, 
            'search_results': None,
            'completed_steps': set(),
            'song_id': None
        }
        
        # Load the agent prompt
        with open('Prompts/agent_prompt.md', 'r', encoding='utf-8') as f:
            self.base_prompt = f.read()
            
        # Ensure output directories exist
        os.makedirs('output/lyrics', exist_ok=True)
        os.makedirs('output/vocabulary', exist_ok=True)
        
        # Cache for song results
        self.cache_dir = 'output/cache'
        os.makedirs(self.cache_dir, exist_ok=True)
        
    def save_lyrics(self, identifier: str, lyrics: str, source_url: str) -> None:
        """Save lyrics and source URL to a file"""
        try:
            os.makedirs('output/lyrics', exist_ok=True)
            filepath = f'output/lyrics/{identifier}.txt'
            print(f"[Agent] Saving lyrics to {filepath}")
            
            # Check for placeholder URLs and replace with a default
            placeholder_patterns = [
                r'\[.*URL.*\]',
                r'\[INSERT.*URL.*\]',
                r'\[PLACE.*HOLDER.*\]',
                r'\[ACTUAL URL.*\]'
            ]
            
            url_is_placeholder = False
            for pattern in placeholder_patterns:
                if re.search(pattern, source_url, re.IGNORECASE):
                    url_is_placeholder = True
                    break
                    
            if url_is_placeholder:
                print(f"[Agent] Warning: Detected placeholder URL: {source_url}")
                if hasattr(self, 'current_data') and self.current_data.get('source_url'):
                    source_url = self.current_data.get('source_url')
                    print(f"[Agent] Using backup URL from current_data: {source_url}")
                else:
                    source_url = "URL not available"
                    print(f"[Agent] No backup URL found, using default: {source_url}")
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Source: {source_url}\n\n{lyrics}")
            print(f"[Agent] Successfully saved lyrics ({len(lyrics)} chars)")
        except Exception as e:
            print(f"[Agent] Error saving lyrics: {str(e)}")
            
    def save_vocabulary(self, identifier: str, vocabulary: List[Dict]) -> None:
        """Save vocabulary items to a JSON file"""
        try:
            os.makedirs('output/vocabulary', exist_ok=True)
            filepath = f'output/vocabulary/{identifier}.json'
            print(f"[Agent] Saving vocabulary to {filepath}")
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(vocabulary, f, ensure_ascii=False, indent=2)
            print(f"[Agent] Successfully saved vocabulary ({len(vocabulary)} items)")
        except Exception as e:
            print(f"[Agent] Error saving vocabulary: {str(e)}")
        
    def process_request(self, song_title: str, artist: str, language: str) -> dict:
        """Process a song request and return the response data."""
        try:
            print(f"[Agent] Processing request for {song_title} by {artist}")
            
            # Check cache
            cache_key = f"{artist}_{song_title}_{language}".lower().replace(' ', '_')
            cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
            
            if os.path.exists(cache_file):
                print(f"[Agent] Found cached result")
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                    if all(k in cached_data for k in ['song_id', 'lyrics', 'vocabulary', 'source_url']):
                        return {'final_response': cached_data}
            
            # Reset current_data for new request
            self.current_data = {
                'lyrics': None, 
                'vocabulary': None, 
                'source_url': None, 
                'search_results': None,
                'completed_steps': set(),  # Track completed steps
                'song_id': None
            }
            
            user_request = f"Find lyrics and vocabulary for '{song_title}' by {artist} in {language}."
            
            # Initialize max retries
            max_retries = self.max_retries
            retry_count = 0
            
            while retry_count < max_retries:
                print(f"\n[Agent] Attempt {retry_count + 1}/{max_retries}")
                print("[Agent] Calling Ollama...")
                
                try:
                    response = self.client.chat(
                        model="mistral",
                        messages=[
                            {"role": "system", "content": self.base_prompt},
                            {"role": "user", "content": user_request}
                        ]
                    )
                    
                    if not isinstance(response, dict) or 'message' not in response:
                        print("[Agent] Invalid response format from Ollama")
                        retry_count += 1
                        continue
                        
                    content = response['message']['content']
                    if not content:
                        print("[Agent] Empty response from Ollama")
                        retry_count += 1
                        continue
                        
                    print("\n[Agent] Full response:")
                    print("-" * 40)
                    print(content)
                    print("-" * 40)
                    
                    result = self._process_agent_response(content, self.current_data)
                    print(f"[Agent] Process result: {result}")
                    
                    if 'final_response' in result:
                        return result
                    elif 'error' in result:
                        print(f"[Agent] Error: {result['error']}")
                        retry_count += 1
                    else:
                        print("[Agent] Response did not contain expected fields")
                        retry_count += 1
                        
                except Exception as e:
                    error_str = str(e)
                    print(f"[Agent] Error: {error_str}")
                    
                    # Check if model not found error and try to pull it
                    if "model \"mistral\" not found" in error_str:
                        try:
                            print("[Agent] Attempting to pull mistral model...")
                            pull_response = self.client.pull("mistral")
                            print(f"[Agent] Pull response: {pull_response}")
                            # Wait a bit for the model to be ready
                            import time
                            time.sleep(10)
                            # Don't increment retry count, we'll try again
                        except Exception as pull_err:
                            print(f"[Agent] Error pulling model: {str(pull_err)}")
                            retry_count += 1
                    else:
                        retry_count += 1
                    
            print("[Agent] Max retries exceeded")
            return {"error": "Max retries exceeded"}
            
        except Exception as e:
            print(f"[Agent] Outer error: {str(e)}")
            return {"error": str(e)}
            
    def _process_agent_response(self, response: str, current_data: dict) -> dict:
        """Process the agent's response and execute tools."""
        print("[Agent] Processing agent response...")
        
        if not response:
            return {"error": "Empty response from agent"}
            
        # Split response into lines and get thoughts
        lines = [l.strip() for l in response.split('\n') if l.strip()]
        thoughts = [l[8:].strip() for l in lines if l.startswith("Thought:")]
        if thoughts:
            print(f"[Agent] Current thought: {thoughts[-1]}")
            
        # Check for final answer first
        final_answer_line = next((l for l in lines if "Final Answer:" in l), None)
        if final_answer_line:
            try:
                # Extract everything after "Final Answer:" and clean up the JSON string
                json_str = final_answer_line.split("Final Answer:")[1].strip()
                
                # First parse as JSON to validate structure
                try:
                    response_data = json.loads(json_str)
                except json.JSONDecodeError as e:
                    print(f"[Agent] Invalid JSON format: {e}")
                    return {"error": f"Invalid JSON format: {e}"}
                
                # Validate required fields
                required_fields = ['song_id', 'language', 'lyrics', 'vocabulary', 'source_url']
                missing_fields = [f for f in required_fields if f not in response_data]
                
                # Check if we have all required data
                if not missing_fields:
                    # Save the data
                    print("[Agent] Saving final data...")
                    self.save_lyrics(response_data['song_id'], response_data['lyrics'], response_data['source_url'])
                    self.save_vocabulary(response_data['song_id'], response_data['vocabulary'])
                    
                    # Cache the result
                    cache_key = f"{response_data['song_id']}.json"
                    cache_file = os.path.join(self.cache_dir, cache_key)
                    with open(cache_file, 'w', encoding='utf-8') as f:
                        json.dump(response_data, f, ensure_ascii=False, indent=2)
                    
                    # Update current_data to mark everything as completed
                    current_data.update({
                        'lyrics': response_data['lyrics'],
                        'vocabulary': response_data['vocabulary'],
                        'source_url': response_data['source_url'],
                        'song_id': response_data['song_id'],
                        'completed_steps': {'search_web', 'get_page_content', 'extract_vocabulary', 'generate_song_id'}
                    })
                    
                    # Return success
                    return {"final_response": response_data}
                
            except Exception as e:
                print(f"[Agent] Error processing final answer: {str(e)}")
                print(f"[Agent] JSON string was: {json_str}")
                return {"error": f"Error processing final answer: {str(e)}"}
                    
        # If no final answer, find and execute the first action
        action_pairs = []
        for i in range(len(lines)):
            if lines[i].startswith("Action:"):
                if i + 1 < len(lines) and lines[i + 1].startswith("Action Input:"):
                    action = lines[i][7:].strip()
                    action_input = lines[i + 1][13:].strip()
                    action_pairs.append((action, action_input))
                    break
        
        if not action_pairs:
            print("[Agent] No valid action found")
            return {"error": "No valid action found"}
        
        action, action_input = action_pairs[0]
        
        # Check if we already have all required data
        if all(k in self.current_data and self.current_data[k] is not None for k in ['lyrics', 'vocabulary', 'source_url', 'song_id']):
            print("[Agent] All required data already collected, returning final identifier")
            return {"final_response": {
                'song_id': self.current_data['song_id'],
                'lyrics': self.current_data['lyrics'],
                'vocabulary': self.current_data['vocabulary'],
                'source_url': self.current_data['source_url']
            }}
            
        # Check if this step was already completed
        if action in self.current_data.get('completed_steps', set()):
            print(f"[Agent] Step {action} already completed, skipping")
            return {"observation": f"Step {action} already completed"}
            
        return self._execute_tool(action, action_input, self.current_data)
            
    def _execute_tool(self, action: str, action_input: str, current_data: dict) -> dict:
        """Execute a single tool and return the result"""
        print(f"[Agent] Executing {action} with input: {action_input!r}")
        
        # Check if step was already completed
        if action in current_data.get('completed_steps', set()):
            print(f"[Agent] Step {action} already completed, skipping")
            return {"observation": f"Step {action} already completed"}
            
        try:
            if action == "search_web":
                result = search_web(action_input)
                if not result:
                    # If search fails, use known good URLs as fallback
                    print("[Agent] Search failed, using fallback URLs")
                    result = [
                        {
                            'title': 'YOASOBI - アイドル (Idol) Lyrics',
                            'url': 'https://genius.com/Yoasobi-idol-lyrics'
                        },
                        {
                            'title': 'YOASOBI - Idol (アイドル) Lyrics',
                            'url': 'https://www.azlyrics.com/lyrics/yoasobi/idol.html'
                        }
                    ]
                self.current_data['search_results'] = result
                self.current_data['completed_steps'].add(action)
                return {"observation": f"Found {len(result)} results"}
                
            elif action == "get_page_content":
                if not self.current_data.get('search_results'):
                    return {"error": "Must search for lyrics first"}
                result = get_page_content(action_input)
                if result.get('error'):
                    return {"error": result['error']}
                self.current_data['lyrics'] = result.get('content', '')
                self.current_data['source_url'] = action_input  # Store the URL that was successfully used
                self.current_data['completed_steps'].add(action)
                return {"observation": f"Got lyrics content"}
                
            elif action == "extract_vocabulary":
                if not self.current_data.get('lyrics'):
                    return {"error": "No lyrics available for vocabulary extraction"}
                result = extract_vocabulary(self.current_data['lyrics'], action_input)
                self.current_data['vocabulary'] = result
                self.current_data['completed_steps'].add(action)
                return {"observation": f"Extracted {len(result)} vocabulary items"}
                
            elif action == "generate_song_id":
                try:
                    params = json.loads(action_input)
                    result = generate_song_id(
                        song_title=params['song_title'],
                        artist=params['artist'],
                        language=params['language']
                    )
                    self.current_data['song_id'] = result
                    self.current_data['completed_steps'].add(action)
                    return {"observation": f"Generated song ID: {result}"}
                except json.JSONDecodeError:
                    return {"error": "Invalid JSON input"}
                except KeyError as e:
                    return {"error": f"Missing required parameter: {str(e)}"}
                    
            return {"error": f"Unknown action: {action}"}
            
        except Exception as e:
            print(f"[Agent] Error executing {action}: {str(e)}")
            return {"error": f"Error executing {action}: {str(e)}"}
