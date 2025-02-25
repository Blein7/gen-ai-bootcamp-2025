import os
from youtube_transcript_api import YouTubeTranscriptApi
from typing import Optional, List, Dict

class YouTubeTranscriptDownloader:
    def __init__(self, languages: List[str] = ["ja", "en"]):
        self.languages = languages
        
    def extract_video_id(self, url: str) -> Optional[str]:
        """
        Extract video ID from YouTube URL
       
        Args:
            url (str): YouTube URL
           
        Returns:
            Optional[str]: Video ID if found, None otherwise
        """
        if "v=" in url:
            return url.split("v=")[1][:11]
        elif "youtu.be/" in url:
            return url.split("youtu.be/")[1][:11]
        return None
        
    def get_transcript(self, video_id: str) -> Optional[List[Dict]]:
        """
        Download YouTube Transcript
       
        Args:
            video_id (str): YouTube video ID or URL
           
        Returns:
            Optional[List[Dict]]: Transcript if successful, None otherwise
        """
        # Extract video ID if full URL is provided
        if "youtube.com" in video_id or "youtu.be" in video_id:
            video_id = self.extract_video_id(video_id)
           
        if not video_id:
            print("Invalid video ID or URL")
            return None
        print(f"Downloading transcript for video ID: {video_id}")
       
        try:
            return YouTubeTranscriptApi.get_transcript(video_id, languages=self.languages)
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return None
    
    def get_versioned_filename(self, base_path: str) -> str:
        """
        Get a versioned filename if the file already exists
        
        Args:
            base_path (str): Base file path without extension
            
        Returns:
            str: Versioned file path
        """
        if not os.path.exists(f"{base_path}.txt"):
            return f"{base_path}.txt"
            
        version = 1
        while os.path.exists(f"{base_path} ({version}).txt"):
            version += 1
            
        return f"{base_path} ({version}).txt"
            
    def save_transcript(self, transcript: List[Dict], filename: str) -> bool:
        """
        Save transcript to file with versioning
       
        Args:
            transcript (List[Dict]): Transcript data
            filename (str): Output filename (without extension)
           
        Returns:
            bool: True if successful, False otherwise
        """
        # Use absolute path based on the location of this script
        directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "transcripts")
        print(f"Using absolute directory path: {directory}")
        
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")
       
        # Create base path without extension
        base_path = os.path.join(directory, filename)
        
        # Get versioned filename
        versioned_filename = self.get_versioned_filename(base_path)
        print(f"Saving transcript to {versioned_filename}")
       
        try:
            with open(versioned_filename, 'w', encoding='utf-8') as f:
                print("Opened file for writing")
                for entry in transcript:
                    f.write(f"{entry['text']}\n")
                print("Finished writing to file")
            print(f"Transcript saved successfully to {versioned_filename}")
            return True
        except Exception as e:
            print(f"Error saving transcript: {str(e)}")
            return False

if __name__ == "__main__":
    video_url = "https://www.youtube.com/watch?v=sY7L5cfCWno&list=PLkGU7DnOLgRMl-h4NxxrGbK-UdZHIXzKQ"
    main(video_url, print_transcript=True)