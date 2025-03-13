import json
import os
from typing import Dict, List, Optional
from datetime import datetime

class QuestionHistory:
    def __init__(self):
        """Initialize question history manager"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.history_file = os.path.join(current_dir, 'question_history.json')
        self._load_history()
    
    def _load_history(self):
        """Load question history from file"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            else:
                self.history = []
        except Exception as e:
            print(f"Error loading history: {str(e)}")
            self.history = []
    
    def _save_history(self):
        """Save question history to file"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving history: {str(e)}")
    
    def add_question(self, question: Dict, section: int, topic: str):
        """Add a new question to history"""
        try:
            # Create history entry with metadata
            entry = {
                "id": len(self.history),
                "timestamp": datetime.now().isoformat(),
                "section": section,
                "topic": topic,
                "question": question
            }
            
            # Add to history and save
            self.history.append(entry)
            self._save_history()
            return entry["id"]
        except Exception as e:
            print(f"Error adding question to history: {str(e)}")
            return None
    
    def get_questions(self, section: Optional[int] = None, topic: Optional[str] = None) -> List[Dict]:
        """Get questions from history with optional filters"""
        try:
            filtered = self.history
            
            if section is not None:
                filtered = [q for q in filtered if q["section"] == section]
            
            if topic is not None:
                filtered = [q for q in filtered if q["topic"] == topic]
            
            return filtered
        except Exception as e:
            print(f"Error getting questions from history: {str(e)}")
            return []
    
    def get_question_by_id(self, question_id: int) -> Optional[Dict]:
        """Get a specific question by ID"""
        try:
            for question in self.history:
                if question["id"] == question_id:
                    return question
            return None
        except Exception as e:
            print(f"Error getting question by ID: {str(e)}")
            return None
