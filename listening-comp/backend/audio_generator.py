import json
import os
import tempfile
import subprocess
from typing import Dict, List, Optional
import boto3
from datetime import datetime
import uuid

class AudioGenerator:
    def __init__(self):
        """Initialize the audio generator with Bedrock and Polly clients"""
        self.bedrock_client = boto3.client('bedrock-runtime', region_name="us-east-1")
        self.polly_client = boto3.client('polly', region_name="us-east-1")
        
        # Define available Japanese standard voices by gender
        self.voices = {
            "male": "Takumi",
            "female": "Mizuki",
            "announcer": "Takumi"
        }
        
        # Create audio output directory if it doesn't exist
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.audio_dir = os.path.join(project_root, "audio")
        try:
            os.makedirs(self.audio_dir, exist_ok=True)
            print(f"Audio directory created/verified at: {self.audio_dir}")
        except OSError as e:
            print(f"Error creating audio directory: {str(e)}")
        
        # Verify voices are available
        try:
            voices = self.polly_client.describe_voices(LanguageCode='ja-JP')
            available_voices = {voice['Id'] for voice in voices['Voices']}
            print(f"Available Japanese voices: {available_voices}")
            
            # Default to first available voice if preferred voices not available
            if not any(voice in available_voices for voice in self.voices.values()):
                default_voice = next(iter(available_voices))
                self.voices = {
                    "male": default_voice,
                    "female": default_voice,
                    "announcer": default_voice
                }
        except Exception as e:
            print(f"Error verifying voices: {str(e)}")
        
        # Create temp directory if it doesn't exist
        self.temp_dir = os.path.join(project_root, "temp")
        try:
            os.makedirs(self.temp_dir, exist_ok=True)
            print(f"Temp directory created/verified at: {self.temp_dir}")
        except OSError as e:
            print(f"Error creating temp directory: {str(e)}")
    
    def _convert_to_conversation_format(self, question: Dict) -> Dict:
        """Convert question into a format with speaker roles using Bedrock"""
        # Prepare the prompt for conversation formatting
        messages = [{
            "role": "user",
            "content": [{
                "text": f"""
                Convert this JLPT listening question into a natural conversation format with clear speaker roles.
                Include gender for each speaker (excluding the announcer).
                
                Original Question:
                Introduction: {question.get('introduction', '')}
                Conversation: {question.get('conversation', '')}
                Question: {question.get('question', '')}
                
                Format the output as a JSON with this structure:
                {{
                    "announcer_intro": "introduction text",
                    "conversation": [
                        {{"speaker": "name", "gender": "male/female", "text": "dialogue"}},
                        ...
                    ],
                    "announcer_question": "question text"
                }}
                
                Make sure to:
                1. Keep all Japanese text as is
                2. Split the conversation naturally between speakers
                3. Assign appropriate genders based on context
                4. Include honorifics and speaking styles appropriate for each speaker
                5. Limit to only male and female genders to match available voices
                """
            }]
        }]
        
        try:
            response = self.bedrock_client.converse(
                modelId="amazon.nova-micro-v1:0",
                messages=messages,
                inferenceConfig={
                    "temperature": 0.5,
                    "topP": 0.9,
                    "maxTokens": 1000
                }
            )
            
            # Extract the JSON part from Nova's response
            result = response['output']['message']['content'][0]['text']
            json_start = result.find('{')
            json_end = result.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = result[json_start:json_end]
                return json.loads(json_str)
            return None
            
        except Exception as e:
            print(f"Error converting to conversation format: {str(e)}")
            return None
    
    def _get_voice_for_gender(self, gender: str) -> str:
        """Get appropriate voice ID for a given gender"""
        gender = gender.lower()
        return self.voices.get(gender, self.voices["announcer"])
    
    def _generate_audio_segment(self, text: str, output_file: str, voice_id: str) -> bool:
        """Generate audio segment using Amazon Polly"""
        try:
            # Check if voice_id is available and use Japanese voice if not
            if voice_id not in ["Takumi", "Mizuki"]:
                voice_id = self.voices["male"] if voice_id in ["Matthew", "Justin"] else self.voices["female"]
                print(f"Substituting non-Japanese voice with {voice_id}")
            
            response = self.polly_client.synthesize_speech(
                Text=text,
                OutputFormat='mp3',
                VoiceId=voice_id,
                LanguageCode='ja-JP',
                Engine='standard'  # Use standard engine for Japanese voices
            )
            
            # Save to temporary file
            with open(output_file, 'wb') as f:
                f.write(response['AudioStream'].read())
            return True
        except Exception as e:
            print(f"Error generating audio segment with voice {voice_id}: {str(e)}")
            # Try with default announcer voice if the specified voice fails
            if voice_id != self.voices["announcer"]:
                print(f"Retrying with announcer voice {self.voices['announcer']}")
                return self._generate_audio_segment(text, output_file, self.voices["announcer"])
            return False
    
    def _generate_silence(self, duration_ms: int, output_file: str) -> bool:
        """Generate a silent audio segment using ffmpeg"""
        try:
            # Use Docker container's ffmpeg
            ffmpeg_path = "/usr/bin/ffmpeg"
            
            if not os.path.exists(ffmpeg_path):
                print(f"ffmpeg not found at {ffmpeg_path}")
                return False
            
            # Generate silence using ffmpeg
            cmd = [
                ffmpeg_path,
                '-y',
                '-f', 'lavfi',
                '-i', f'anullsrc=r=24000:cl=mono',
                '-t', f'{duration_ms/1000}',  # Convert ms to seconds
                '-acodec', 'libmp3lame',
                '-b:a', '128k',
                output_file
            ]
            
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False
            )
            
            if process.returncode != 0:
                print(f"Error generating silence: {process.stderr}")
                return False
                
            return True
            
        except Exception as e:
            print(f"Error generating silence: {str(e)}")
            return False
    
    def _combine_audio_files(self, audio_files: List[str], output_file: str) -> bool:
        """Combine multiple audio files using ffmpeg"""
        try:
            if not audio_files:
                print("No audio files to combine")
                return False
                
            if len(audio_files) == 1:
                # If only one file, just copy it to the output location
                import shutil
                shutil.copy2(audio_files[0], output_file)
                # Clean up temporary file
                os.remove(audio_files[0])
                return True
            
            # Create output directory if it doesn't exist
            output_dir = os.path.dirname(output_file)
            os.makedirs(output_dir, exist_ok=True)
            
            # Create a temporary file list for ffmpeg
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                for audio_file in audio_files:
                    # Verify file exists and convert path for ffmpeg
                    if not os.path.exists(audio_file):
                        print(f"Audio file not found: {audio_file}")
                        return False
                    # Use absolute path with forward slashes
                    abs_path = os.path.abspath(audio_file).replace('\\', '/')
                    f.write(f"file '{abs_path}'\n")
                file_list = f.name
            
            try:
                print(f"Running ffmpeg with file list: {file_list}")
                with open(file_list, 'r', encoding='utf-8') as f:
                    print("File list contents:")
                    print(f.read())
                
                # Use Docker container's ffmpeg
                ffmpeg_path = "/usr/bin/ffmpeg"
                
                if not os.path.exists(ffmpeg_path):
                    print(f"ffmpeg not found at {ffmpeg_path}")
                    return False
                
                # Build the ffmpeg command with proper quoting
                cmd = [
                    ffmpeg_path,
                    '-y',  # Overwrite output file if it exists
                    '-f', 'concat',
                    '-safe', '0',
                    '-i', file_list,
                    '-c', 'copy',  # Copy codec without re-encoding
                    output_file
                ]
                
                print(f"Running command: {' '.join(cmd)}")
                
                # Run ffmpeg directly without PowerShell
                process = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=False,  # Don't raise exception on non-zero return
                    cwd=os.path.dirname(output_file)  # Set working directory to output location
                )
                
                if process.returncode != 0:
                    print(f"ffmpeg stdout: {process.stdout}")
                    print(f"ffmpeg stderr: {process.stderr}")
                    return False
                
                # Clean up temporary files
                os.unlink(file_list)
                for file in audio_files:
                    try:
                        os.remove(file)
                    except Exception as e:
                        print(f"Error removing temporary file {file}: {str(e)}")
                
                return True
                
            except Exception as e:
                print(f"Error running ffmpeg: {str(e)}")
                # Clean up temporary files
                try:
                    os.unlink(file_list)
                except:
                    pass
                for file in audio_files:
                    try:
                        os.remove(file)
                    except:
                        pass
                return False
                
        except Exception as e:
            print(f"Error combining audio files: {str(e)}")
            # Clean up any temporary files
            for file in audio_files:
                try:
                    os.remove(file)
                except:
                    pass
            return False
    
    def generate_audio(self, question: Dict) -> Optional[str]:
        """Generate audio for a question by converting it to a conversation format"""
        try:
            # Generate a unique filename for this question
            output_file = os.path.join(self.audio_dir, f"question_{uuid.uuid4()}.mp3")
            
            # Convert question to conversation format
            conversation = self._convert_to_conversation_format(question)
            if not conversation:
                print("Failed to convert question to conversation format")
                return None
            
            audio_files = []
            try:
                # Generate intro audio with announcer voice
                intro_voice = self.voices["announcer"]
                intro_text = conversation['announcer_intro']
                intro_file = os.path.join(self.temp_dir, f"intro_{uuid.uuid4()}.mp3")
                if not self._generate_audio_segment(intro_text, intro_file, intro_voice):
                    print("Failed to generate intro audio")
                    return None
                audio_files.append(intro_file)
                
                # Add a longer pause (2 seconds) after intro
                silence_file = os.path.join(self.temp_dir, f"silence_{uuid.uuid4()}.mp3")
                if not self._generate_silence(2000, silence_file):
                    print("Failed to generate silence after intro")
                    return None
                audio_files.append(silence_file)
                
                # Generate conversation audio alternating between voices
                for i, segment in enumerate(conversation['conversation'], 1):
                    gender = segment.get('gender', 'male').lower()
                    voice = self._get_voice_for_gender(gender)
                    audio_file = os.path.join(self.temp_dir, f"segment_{i}_{uuid.uuid4()}.mp3")
                    if not self._generate_audio_segment(segment['text'], audio_file, voice):
                        print(f"Failed to generate audio for segment {i}")
                        return None
                    audio_files.append(audio_file)
                    
                    # Add a shorter pause (1 second) between conversation parts
                    if i < len(conversation['conversation']):
                        silence_file = os.path.join(self.temp_dir, f"silence_{i}_{uuid.uuid4()}.mp3")
                        if not self._generate_silence(1000, silence_file):
                            print("Failed to generate silence between segments")
                            return None
                        audio_files.append(silence_file)
                
                # Generate announcer question
                announcer_voice = self.voices["announcer"]
                announcer_question_text = conversation['announcer_question']
                announcer_question_file = os.path.join(self.temp_dir, f"announcer_question_{uuid.uuid4()}.mp3")
                if not self._generate_audio_segment(announcer_question_text, announcer_question_file, announcer_voice):
                    print("Failed to generate announcer question audio")
                    return None
                audio_files.append(announcer_question_file)
                
                # Combine all audio segments
                if not self._combine_audio_files(audio_files, output_file):
                    print("Failed to combine audio files")
                    return None
                
                return output_file
                
            except Exception as e:
                print(f"Error generating audio segments: {str(e)}")
                # Clean up any temporary files
                for file in audio_files:
                    try:
                        os.remove(file)
                    except:
                        pass
                return None
                
        except Exception as e:
            print(f"Error generating audio: {str(e)}")
            return None
