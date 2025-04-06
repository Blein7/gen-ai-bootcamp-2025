import re
import json
import os
from typing import Dict, Optional
from datetime import datetime

class SongIdManager:
    def __init__(self):
        self.db_file = 'output/song_registry.json'
        os.makedirs('output', exist_ok=True)
        self._ensure_db()
    
    def _ensure_db(self):
        """Create the registry file if it doesn't exist"""
        if not os.path.exists(self.db_file):
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump({}, f)
    
    def _load_registry(self) -> Dict:
        """Load the song registry"""
        with open(self.db_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_registry(self, registry: Dict):
        """Save the song registry"""
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
    
    def _sanitize_string(self, s: str) -> str:
        """Convert string to safe format for ID"""
        # Convert to lowercase and replace spaces with underscores
        s = s.lower().strip()
        # Remove non-alphanumeric characters (except underscores)
        s = re.sub(r'[^\w\s-]', '', s)
        # Replace spaces with underscores
        s = re.sub(r'[-\s]+', '_', s)
        return s
    
    def generate_id(self, song_title: str, artist: str, language: str) -> str:
        """Generate a unique ID for a song"""
        # Create base ID
        base_id = f"{self._sanitize_string(artist)}_{self._sanitize_string(song_title)}_{self._sanitize_string(language)}"
        
        # Load registry
        registry = self._load_registry()
        
        # Check if song already exists
        for song_id, info in registry.items():
            if (info['artist'].lower() == artist.lower() and 
                info['title'].lower() == song_title.lower() and 
                info['language'].lower() == language.lower()):
                return song_id
        
        # If not found, create new entry
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_id = f"{base_id}_{timestamp}"
        
        # Add to registry
        registry[new_id] = {
            'artist': artist,
            'title': song_title,
            'language': language,
            'created_at': timestamp
        }
        
        # Save updated registry
        self._save_registry(registry)
        
        return new_id
    
    def get_song_info(self, song_id: str) -> Optional[Dict]:
        """Get information about a song by its ID"""
        registry = self._load_registry()
        return registry.get(song_id)

# Singleton instance
_manager = SongIdManager()

def generate_song_id(song_title: str, artist: str, language: str = "Japanese") -> str:
    """Generate a unique ID for a song"""
    return _manager.generate_id(song_title, artist, language)

def get_song_info(song_id: str) -> Optional[Dict]:
    """Get information about a song by its ID"""
    return _manager.get_song_info(song_id)
