import google.generativeai as genai
import os
from dotenv import load_dotenv
import json

load_dotenv()

class RAGChatbot:
    def __init__(self, schemes_data):
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.schemes_data = schemes_data
        self.create_context()
    
    def create_context(self):
        """Create searchable context from schemes"""
        self.context = ""
        for scheme in self.schemes_data:
            self.context += f"""
Scheme: {scheme['title']}
Category: {scheme['category']}
Description: {scheme['description']}
Eligibility: {scheme['eligibility']}
Benefits: {scheme['benefits']}
---
"""
    
    def search_schemes(self, query):
        """Simple keyword search"""
        query_lower = query.lower()
        relevant = []
        
        for scheme in self.schemes_data:
            text = f"{scheme['title']} {scheme['description']} {scheme['eligibility']} {scheme['benefits']}".lower()
            if any(word in text for word in query_lower.split()):
                relevant.append(scheme)
        
        return relevant[:3]
    
    def chat(self, user_query):
        """Chat with context"""
        relevant = self.search_schemes(user_query)
        
        if relevant:
            context = "Relevant schemes:\n"
            for s in relevant:
                context += f"\n{s['title']}: {s['description']}\nBenefits: {s['benefits']}\n"
        else:
            context = self.context[:2000]
        
        prompt = f"""You are a helpful assistant for government schemes in India.
Answer based on the scheme information provided.
Use simple language.

Schemes:
{context}

Question: {user_query}

Answer:"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Sorry, error: {str(e)}"