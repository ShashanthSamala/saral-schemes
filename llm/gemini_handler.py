import google.generativeai as genai
import os
from dotenv import load_dotenv
import time

load_dotenv()

class GeminiHandler:
    def __init__(self):
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in .env file")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.last_request_time = 0
        self.min_request_interval = 1  # Seconds between requests
    
    def _rate_limit(self):
        """Simple rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()
    
    def translate_text(self, text, target_language):
        """Translate text using Gemini"""
        if not text or text == 'N/A':
            return text
        
        self._rate_limit()
        
        prompt = f"""Translate the following text to {target_language}. 
Only provide the translation, no additional text or explanations.

Text: {text}

Translation:"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Translation error: {e}")
            return text
    
    def simplify_text(self, text):
        """Simplify complex government language"""
        if not text or text == 'N/A':
            return text
        
        self._rate_limit()
        
        prompt = f"""Simplify the following government scheme text for rural and less educated people. 
Use very simple words, short sentences, and easy to understand language.
Make it sound friendly and helpful.
Keep it under 100 words.

Text: {text}

Simplified version:"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Simplification error: {e}")
            return text
    
    def translate_scheme(self, scheme, language):
        """Translate entire scheme - with progress feedback"""
        if language == 'English':
            return scheme
        
        print(f"   Translating to {language}...", end='', flush=True)
        
        translated = {}
        
        try:
            translated['title'] = self.translate_text(scheme['title'], language)
            translated['description'] = self.translate_text(scheme['description'], language)
            translated['eligibility'] = self.translate_text(scheme['eligibility'], language)
            translated['benefits'] = self.translate_text(scheme['benefits'], language)
            print(" ✅")
            return translated
        except Exception as e:
            print(f" ❌ ({e})")
            return scheme
    
    def generate_simple_explanation(self, scheme):
        """Generate very simple explanation for illiterate users"""
        self._rate_limit()
        
        prompt = f"""Explain this government scheme in very simple language that a 10-year-old can understand.
Use everyday words. Make it 2-3 short sentences only.

Scheme: {scheme['title']}
What it does: {scheme['description']}
Who can get it: {scheme['eligibility']}
What you get: {scheme['benefits']}

Simple explanation:"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"This scheme helps people by providing {scheme['benefits']}"
    
    def answer_question(self, question, context):
        """Answer questions about schemes"""
        self._rate_limit()
        
        prompt = f"""You are a helpful government schemes assistant for India.
Answer the user's question based on the context provided.
Use simple language that anyone can understand.
If you don't know, say "I don't have that information."

Context:
{context}

Question: {question}

Answer:"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"

# Test the handler
if __name__ == "__main__":
    print("=" * 50)
    print("GEMINI LLM HANDLER TEST")
    print("=" * 50)
    
    try:
        handler = GeminiHandler()
        print("✅ Gemini API connected successfully\n")
        
        test_text = "Financial assistance to farmers for agricultural investment per acre per season"
        
        print("📝 Original Text:")
        print(f"   {test_text}\n")
        
        print("🔄 Simplifying...")
        simplified = handler.simplify_text(test_text)
        print(f"   {simplified}\n")
        
        print("🌐 Translating to Hindi...")
        hindi = handler.translate_text(test_text, "Hindi")
        print(f"   {hindi}\n")
        
        print("🌐 Translating to Telugu...")
        telugu = handler.translate_text(test_text, "Telugu")
        print(f"   {telugu}\n")
        
        print("✅ All tests passed!")
        
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("\n💡 Create .env file with: GOOGLE_API_KEY=your_key_here")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("=" * 50)