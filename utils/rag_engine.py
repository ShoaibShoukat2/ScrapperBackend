"""
RAG (Retrieval-Augmented Generation) Engine for Program Chatbot
File: utils/rag_engine.py
"""
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os


class RAGEngine:
    """
    RAG engine for context-aware program recommendations
    Uses TF-IDF for embeddings and cosine similarity for retrieval
    """
    
    def __init__(self, programs_df=None):
        self.programs_df = programs_df
        self.vectorizer = TfidfVectorizer(
            max_features=500,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.program_vectors = None
        self.is_trained = False
        
        if programs_df is not None and len(programs_df) > 0:
            self.train()
    
    def train(self):
        """Train the RAG model on program descriptions"""
        if self.programs_df is None or len(self.programs_df) == 0:
            print("No programs to train on")
            return False
        
        # Combine relevant text fields for embedding
        self.programs_df['combined_text'] = (
            self.programs_df['program_name'].fillna('') + ' ' +
            self.programs_df['university'].fillna('') + ' ' +
            self.programs_df['degree_type'].fillna('') + ' ' +
            self.programs_df['description'].fillna('') + ' ' +
            self.programs_df['country'].fillna('') + ' ' +
            self.programs_df['requirements'].fillna('')
        )
        
        # Generate TF-IDF vectors
        texts = self.programs_df['combined_text'].tolist()
        self.program_vectors = self.vectorizer.fit_transform(texts)
        self.is_trained = True
        
        print(f"✓ RAG Engine trained on {len(self.programs_df)} programs")
        return True
    
    def update_programs(self, programs_df):
        """Update the programs and retrain"""
        self.programs_df = programs_df
        return self.train()
    
    def search(self, query, top_k=5):
        """
        Search for relevant programs based on query
        Returns top_k most relevant programs
        """
        if not self.is_trained:
            return []
        
        # Vectorize query
        query_vector = self.vectorizer.transform([query])
        
        # Calculate cosine similarity
        similarities = cosine_similarity(query_vector, self.program_vectors).flatten()
        
        # Get top k indices
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        # Filter out very low similarities (threshold: 0.1)
        filtered_indices = [idx for idx in top_indices if similarities[idx] > 0.1]
        
        # Return relevant programs with scores
        results = []
        for idx in filtered_indices:
            program = self.programs_df.iloc[idx].to_dict()
            program['relevance_score'] = float(similarities[idx])
            results.append(program)
        
        return results
    
    def generate_response(self, query, context_programs):
        """
        Generate a response based on query and retrieved programs
        """
        if not context_programs:
            return {
                'response': "I couldn't find any programs matching your query. Could you provide more details about what you're looking for?",
                'programs': []
            }
        
        # Extract key information
        program_names = [p['program_name'] for p in context_programs[:3]]
        universities = [p['university'] for p in context_programs[:3]]
        
        # Generate response
        response = f"I found {len(context_programs)} relevant programs for your query. "
        
        if len(context_programs) > 0:
            response += f"\n\nTop recommendations:\n"
            for i, prog in enumerate(context_programs[:3], 1):
                response += f"\n{i}. {prog['program_name']} at {prog['university']}"
                response += f"\n   - Degree: {prog.get('degree_type', 'N/A')}"
                response += f"\n   - Duration: {prog.get('duration', 'N/A')}"
                response += f"\n   - Tuition: {prog.get('tuition_fee', 'N/A')}"
                response += f"\n   - Country: {prog.get('country', 'N/A')}\n"
        
        return {
            'response': response,
            'programs': context_programs,
            'count': len(context_programs)
        }
    
    def chat(self, message, history=None):
        """
        Main chat interface
        Searches for relevant programs and generates response
        """
        # Search for relevant programs
        relevant_programs = self.search(message, top_k=5)
        
        # Generate response
        result = self.generate_response(message, relevant_programs)
        
        return result

# Alternative: OpenAI-based RAG (if API key is available)
class OpenAIRAGEngine:
    """
    OpenAI-powered RAG engine for more sophisticated responses
    Requires OPENAI_API_KEY environment variable
    """
    
    def __init__(self, programs_df=None):
        self.programs_df = programs_df
        self.openai_available = False
        
        try:
            import openai
            openai.api_key = os.getenv('OPENAI_API_KEY')
            if openai.api_key:
                self.client = openai
                self.openai_available = True
                print("✓ OpenAI API initialized")
        except Exception as e:
            print(f"OpenAI not available: {e}")
            
        # Fallback to TF-IDF
        self.fallback_engine = RAGEngine(programs_df)
    
    def search(self, query, top_k=5):
        """Search using embeddings or fallback to TF-IDF"""
        return self.fallback_engine.search(query, top_k)
    
    def generate_response_with_gpt(self, query, context_programs):
        """Generate response using GPT"""
        if not self.openai_available:
            return self.fallback_engine.generate_response(query, context_programs)
        
        try:
            # Prepare context
            context = "Available programs:\n"
            for prog in context_programs[:5]:
                context += f"- {prog['program_name']} at {prog['university']}\n"
                context += f"  Duration: {prog.get('duration', 'N/A')}, "
                context += f"Tuition: {prog.get('tuition_fee', 'N/A')}\n"
            
            # Call GPT
            response = self.client.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful education advisor assistant. Provide concise, helpful information about study programs."},
                    {"role": "user", "content": f"Context: {context}\n\nUser question: {query}"}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            
            return {
                'response': response.choices[0].message.content,
                'programs': context_programs,
                'count': len(context_programs)
            }
            
        except Exception as e:
            print(f"GPT error: {e}")
            return self.fallback_engine.generate_response(query, context_programs)
    
    def chat(self, message, history=None):
        """Chat interface with GPT fallback"""
        relevant_programs = self.search(message, top_k=5)
        
        if self.openai_available:
            return self.generate_response_with_gpt(message, relevant_programs)
        else:
            return self.fallback_engine.generate_response(message, relevant_programs)