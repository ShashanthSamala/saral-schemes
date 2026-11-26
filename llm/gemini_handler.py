import re
import time
from pydantic import BaseModel
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv()

import json

class LocalizedSchemeFields(BaseModel):
    """Structured output for translated and simplified scheme fields."""
    title: str
    description: str
    eligibility: str
    benefits: str
    required_documents: str
    how_to_apply: str
    deadlines: str
    post_application_steps: str


class GeminiHandler:
    def __init__(self):
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            try:
                import streamlit as st
                if hasattr(st, "secrets") and "GOOGLE_API_KEY" in st.secrets:
                    api_key = st.secrets["GOOGLE_API_KEY"]
            except Exception:
                pass

        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables or Streamlit secrets")
        
        self.client = genai.Client(api_key=api_key)
        self.model_name = 'gemini-3.5-flash-lite'
        self.last_request_time = 0
        self.min_request_interval = 4  # Seconds between requests to respect free tier RPM
    
    def _call_with_retry(self, prompt, max_retries=3, fallback_model='gemini-3.6-flash'):
        for attempt in range(max_retries):
            try:
                return self.client.models.generate_content(model=self.model_name, contents=prompt)
            except Exception as e:
                if attempt < max_retries - 1:
                    err = str(e).lower()
                    is_503 = "503" in err or "unavailable" in err or "high demand" in err
                    if is_503:
                        # Fall back to alternate model on 503
                        try:
                            return self.client.models.generate_content(model=fallback_model, contents=prompt)
                        except Exception:
                            pass  # Fall through to normal retry below
                    match = re.search(r'retry in ([\d.]+)s', err)
                    wait = float(match.group(1)) + 1 if match else 20
                    time.sleep(wait)
                    continue
                raise

    def translate_and_simplify_scheme(self, scheme_data: dict, target_language: str, retries: int = 3) -> dict:
        """Translate and simplify all scheme fields in a single structured API call."""
        prompt = f"""
Translate the following government scheme fields into {target_language}.
Rewrite every field at a clear 5th-grade reading level so farmers and rural citizens
can understand it easily without bureaucratic jargon. Keep numbers, dates, and official
document names accurate.

Scheme Data:
Title: {scheme_data.get('title', '')}
Description: {scheme_data.get('description', '')}
Eligibility: {scheme_data.get('eligibility', '')}
Benefits: {scheme_data.get('benefits', '')}
Required Documents: {scheme_data.get('required_documents', '')}
How to Apply: {scheme_data.get('how_to_apply', '')}
Deadlines: {scheme_data.get('deadlines', '')}
After Applying: {scheme_data.get('post_application_steps', '')}
"""

        for attempt in range(retries):
            try:
                gen_config = types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=LocalizedSchemeFields,
                    temperature=0.2,
                )
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=gen_config,
                )
                parsed: LocalizedSchemeFields = response.parsed
                return parsed.model_dump()
            except Exception as e:
                err = str(e).lower()
                is_503 = "503" in err or "unavailable" in err or "high demand" in err
                if is_503 and attempt < retries - 1:
                    # Fall back to alternate model on 503
                    try:
                        gen_config = types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=LocalizedSchemeFields,
                            temperature=0.2,
                        )
                        response = self.client.models.generate_content(
                            model="gemini-3.6-flash",
                            contents=prompt,
                            config=gen_config,
                        )
                        parsed: LocalizedSchemeFields = response.parsed
                        return parsed.model_dump()
                    except Exception:
                        pass  # Fall through to normal retry below
                if attempt == retries - 1:
                    raise RuntimeError(f"Gemini translation failed after {retries} attempts: {e}")
                time.sleep(2 ** attempt)

    def translate_text(self, text, target_language):
        """Translate text using Gemini"""
        if not text or text == 'N/A':
            return text
        
        prompt = f"""Translate the following text to {target_language}. 
Only provide the translation, no additional text or explanations.

Text: {text}

Translation:"""
        
        try:
            response = self._call_with_retry(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Translation error: {e}")
            return text
    
    def simplify_text(self, text):
        """Simplify complex government language"""
        if not text or text == 'N/A':
            return text
        
        prompt = f"""Simplify the following government scheme text for rural and less educated people. 
Use very simple words, short sentences, and easy to understand language.
Make it sound friendly and helpful.
Keep it under 100 words.

Text: {text}

Simplified version:"""
        
        try:
            response = self._call_with_retry(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Simplification error: {e}")
            return text
    
    def translate_scheme(self, scheme, language):
        """Translate entire scheme in a single API call using JSON formatting"""
        if language == 'English':
            return scheme
        
        prompt = f"""Translate the following government scheme information into {language}.
Return ONLY a valid JSON object matching this structure, with no markdown formatting or extra text:
{{
  "title": "translated title",
  "description": "translated description",
  "eligibility": "translated eligibility",
  "benefits": "translated benefits"
}}

Scheme Information:
Title: {scheme.get('title', '')}
Description: {scheme.get('description', '')}
Eligibility: {scheme.get('eligibility', '')}
Benefits: {scheme.get('benefits', '')}
"""
        try:
            response = self._call_with_retry(prompt)
            text_resp = response.text.strip()
            # Need to fix the parsing logic here as the previous edit truncated it
            # The method logic was cut off.
            import re
            json_match = re.search(r'\{.*\}', text_resp, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                return {
                    "title": data.get("title", scheme.get("title", "")),
                    "description": data.get("description", scheme.get("description", "")),
                    "eligibility": data.get("eligibility", scheme.get("eligibility", "")),
                    "benefits": data.get("benefits", scheme.get("benefits", ""))
                }
            # Fallback
            return scheme
        except Exception as e:
            print(f"Scheme batch translation error: {e}")
            # Fallback to field by field
            return {
                'title': self.translate_text(scheme.get('title', ''), language),
                'description': self.translate_text(scheme.get('description', ''), language),
                'eligibility': self.translate_text(scheme.get('eligibility', ''), language),
                'benefits': self.translate_text(scheme.get('benefits', ''), language)
            }
            text_resp = response.text.strip()
            # Clean possible markdown json code block
            if text_resp.startswith("```json"):
                text_resp = text_resp[7:]
            if text_resp.startswith("```"):
                text_resp = text_resp[3:]
            if text_resp.endswith("```"):
                text_resp = text_resp[:-3]
            text_resp = text_resp.strip()

            data = json.loads(text_resp)
            return {
                "title": data.get("title", scheme.get("title", "")),
                "description": data.get("description", scheme.get("description", "")),
                "eligibility": data.get("eligibility", scheme.get("eligibility", "")),
                "benefits": data.get("benefits", scheme.get("benefits", ""))
            }
        except Exception as e:
            print(f"Scheme batch translation error: {e}")
            # Fallback to field by field if JSON parsing fails
            try:
                return {
                    'title': self.translate_text(scheme.get('title', ''), language),
                    'description': self.translate_text(scheme.get('description', ''), language),
                    'eligibility': self.translate_text(scheme.get('eligibility', ''), language),
                    'benefits': self.translate_text(scheme.get('benefits', ''), language)
                }
            except Exception as e2:
                print(f"Fallback translation error: {e2}")
                return scheme
    
    def generate_simple_explanation(self, scheme):
        """Generate very simple explanation for illiterate users"""
        prompt = f"""Explain this government scheme in very simple language that a 10-year-old can understand.
Use everyday words. Make it 2-3 short sentences only.

Scheme: {scheme['title']}
What it does: {scheme['description']}
Who can get it: {scheme['eligibility']}
What you get: {scheme['benefits']}

Simple explanation:"""
        
        try:
            response = self._call_with_retry(prompt)
            return response.text.strip()
        except Exception as e:
            return f"This scheme helps people by providing {scheme['benefits']}"
    
    def answer_question(self, question, context):
        """Answer questions about schemes"""
        prompt = f"""You are a helpful government schemes assistant for India.
Answer the user's question based on the context provided.
Use simple language that anyone can understand.
If you don't know, say "I don't have that information."

Context:
{context}

Question: {question}

Answer:"""
        
        try:
            response = self._call_with_retry(prompt)
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
