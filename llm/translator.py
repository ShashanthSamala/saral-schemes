import os
from database.db_manager import DatabaseManager
from llm.gemini_handler import GeminiHandler

class SchemeTranslator:
    def __init__(self, db_manager: DatabaseManager = None):
        self.db = db_manager or DatabaseManager()
        self.gemini = None

        # Check if GOOGLE_API_KEY is available before initializing GeminiHandler
        if os.getenv("GOOGLE_API_KEY"):
            try:
                self.gemini = GeminiHandler()
            except Exception as e:
                print(f"Warning: Failed to initialize GeminiHandler: {e}")

    def translate_scheme(self, scheme: dict, target_language: str) -> dict:
        """
        Translate a scheme dict to target_language using caching in SQLite database.
        If target_language is 'English', returns the original scheme.
        If Gemini is unavailable or fails, returns original scheme as fallback.
        """
        if not target_language or target_language == "English":
            return scheme

        scheme_id = scheme.get("id")

        # Check translation cache in DB if scheme has an id
        if scheme_id:
            cached = self.db.get_translation(scheme_id, target_language)
            if cached:
                return {
                    **scheme,
                    "title": cached.get("translated_title") or scheme.get("title", ""),
                    "description": cached.get("translated_description") or scheme.get("description", ""),
                    "eligibility": cached.get("translated_eligibility") or scheme.get("eligibility", ""),
                    "benefits": cached.get("translated_benefits") or scheme.get("benefits", "")
                }

        # If Gemini AI handler is available, perform translation
        if self.gemini:
            try:
                translated = self.gemini.translate_scheme(scheme, target_language)

                # Save to database cache if scheme has an id
                if scheme_id:
                    self.db.save_translation(scheme_id, target_language, {
                        "title": translated.get("title", scheme.get("title", "")),
                        "description": translated.get("description", scheme.get("description", "")),
                        "eligibility": translated.get("eligibility", scheme.get("eligibility", "")),
                        "benefits": translated.get("benefits", scheme.get("benefits", ""))
                    })
                return {
                    **scheme,
                    **translated
                }
            except Exception as e:
                print(f"Translation failed: {e}")

        # Fallback to original scheme
        return scheme
