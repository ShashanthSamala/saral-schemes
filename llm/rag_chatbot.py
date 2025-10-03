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
        self.scheme_index = {}
        
        for idx, scheme in enumerate(self.schemes_data):
            scheme_text = f"""
Scheme {idx + 1}: {scheme['title']}
Category: {scheme['category']}
Description: {scheme['description']}
Eligibility: {scheme['eligibility']}
Benefits: {scheme['benefits']}
---
"""
            self.context += scheme_text
            self.scheme_index[idx] = scheme
    
    def search_schemes(self, query):
        """Simple keyword-based search"""
        query_lower = query.lower()
        relevant_schemes = []
        
        # Keywords to boost
        keywords = query_lower.split()
        
        for scheme in self.schemes_data:
            score = 0
            scheme_text = f"{scheme['title']} {scheme['description']} {scheme['category']} {scheme['eligibility']} {scheme['benefits']}".lower()
            
            # Calculate relevance score
            for keyword in keywords:
                if keyword in scheme_text:
                    score += scheme_text.count(keyword)
            
            if score > 0:
                relevant_schemes.append((score, scheme))
        
        # Sort by score and return top 3
        relevant_schemes.sort(reverse=True, key=lambda x: x[0])
        return [scheme for score, scheme in relevant_schemes[:3]]
    
    def chat(self, user_query):
        """Main chat function with context"""
        # Get relevant schemes
        relevant_schemes = self.search_schemes(user_query)
        
        # Build context from relevant schemes
        if relevant_schemes:
            context = "Here are the most relevant schemes:\n\n"
            for i, scheme in enumerate(relevant_schemes, 1):
                context += f"{i}. {scheme['title']}\n"
                context += f"   Category: {scheme['category']}\n"
                context += f"   Description: {scheme['description']}\n"
                context += f"   Eligibility: {scheme['eligibility']}\n"
                context += f"   Benefits: {scheme['benefits']}\n\n"
        else:
            # Use general context
            context = self.context[:2000]
        
        # Create prompt
        prompt = f"""You are a helpful assistant for government schemes in India, specifically Telangana.
Answer the user's question based on the scheme information provided.
Use simple, friendly language that rural people can understand.
If asked about eligibility, benefits, or how to apply, provide specific details from the schemes.
If you don't find relevant information, suggest related schemes.

Available Schemes:
{context}

User Question: {user_query}

Your Answer (in simple, helpful language):"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Sorry, I'm having trouble right now. Error: {str(e)}"
    
    def get_recommendations(self, user_profile):
        """Recommend schemes based on user profile"""
        prompt = f"""Based on this person's profile, recommend 2-3 most suitable government schemes from the list.
Explain why each scheme is good for them in simple language.

User Profile: {user_profile}

Available Schemes:
{self.context[:1500]}

Your Recommendations:"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return "Unable to generate recommendations right now."
    
    def explain_scheme(self, scheme_title):
        """Explain a specific scheme in detail"""
        # Find the scheme
        scheme = None
        for s in self.schemes_data:
            if scheme_title.lower() in s['title'].lower():
                scheme = s
                break
        
        if not scheme:
            return f"Sorry, I couldn't find a scheme called '{scheme_title}'. Try asking about 'farmer schemes' or 'pension schemes'."
        
        prompt = f"""Explain this government scheme in very simple language:

Scheme Name: {scheme['title']}
Description: {scheme['description']}
Who can get it: {scheme['eligibility']}
Benefits: {scheme['benefits']}

Explain in simple words:
1. What is this scheme?
2. Who should apply?
3. What will they get?
4. Why is it helpful?

Simple Explanation:"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"This scheme is called {scheme['title']}. {scheme['description']} {scheme['benefits']}"

# Test
if __name__ == "__main__":
    print("=" * 50)
    print("RAG CHATBOT TEST")
    print("=" * 50)
    
    try:
        # Load schemes
        with open('data/scraped_schemes.json', 'r', encoding='utf-8') as f:
            schemes = json.load(f)
        
        print(f"✅ Loaded {len(schemes)} schemes\n")
        
        chatbot = RAGChatbot(schemes)
        print("✅ Chatbot initialized\n")
        
        # Test queries
        test_queries = [
            "What schemes are available for farmers?",
            "I am 70 years old. What can I get?",
            "Tell me about Rythu Bandhu scheme"
        ]
        
        for query in test_queries:
            print(f"❓ Question: {query}")
            print(f"💬 Answer: {chatbot.chat(query)}\n")
            print("-" * 50 + "\n")
        
        print("✅ All tests completed!")
        
    except FileNotFoundError:
        print("❌ Error: Run scraper first to generate data/scraped_schemes.json")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("=" * 50)