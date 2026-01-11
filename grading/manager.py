import json
import os
from typing import Dict, Any, Optional

class QuizManager:
    """Manage the storage and retrieval of Quiz objects."""
    
    def __init__(self, storage_path):
        self.storage_path = storage_path

    def save_quiz(self, quiz_data):
        """Save quiz object to storage for the grading engine."""
        data = quiz_data.model_dump() if hasattr(quiz_data, "model_dump") else quiz_data
        
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def load_quiz(self) -> Optional[Dict[str, Any]]:
        """Loads the quiz object from storage"""
        if not os.path.exists(self.storage_path):
            print("Erreur : Aucun fichier de quiz trouvé.")
            return None
            
        with open(self.storage_path, "r", encoding="utf-8") as f:
            return json.load(f)