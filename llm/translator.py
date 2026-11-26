import os
from database.db_manager import DatabaseManager
from llm.gemini_handler import GeminiHandler

class SchemeTranslator:
    def __init__(self, db_manager: DatabaseManager = None):
        self.db = db_manager or DatabaseManager()
        self.gemini = None

        try:
            self.gemini = GeminiHandler()
        except Exception as e:
            print(f"Warning: Failed to initialize GeminiHandler: {e}")

    def get_field_translation(self, scheme_id, language, field, original_text):
        """Get translated field with cache-first logic."""
        if language == "English" or not original_text:
            return original_text
        
        cached = self.db.get_translation(scheme_id, language, field)
        if cached:
            return cached
            
        if self.gemini:
            # Show spinner in app code, not here.
            translated = self.gemini.translate_text(original_text, language)
            self.db.save_translation(scheme_id, language, field, translated)
            return translated
            
        return original_text

