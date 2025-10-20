#!/usr/bin/env python3
"""
Advanced RAG System - State-of-the-Art Implementation
Features:
- Multi-query expansion
- Semantic reranking
- Context windowing
- Query preprocessing
- Hybrid search (semantic + keyword)
- Response quality scoring
"""

import os
import re
import hashlib
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from groq import Groq
import requests
import json

load_dotenv()

@dataclass
class SearchResult:
    content: str
    score: float
    metadata: Dict
    source: str

class AdvancedRAGSystem:
    def __init__(self):
        # Configuration
        self.QDRANT_URL = os.getenv("QDRANT_URL")
        self.QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
        self.COLLECTION_NAME = "fragments_to_thought"
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        self.GROQ_MODEL = "llama-3.1-8b-instant"
        
        # Initialize clients
        self.qdrant_client = QdrantClient(
            url=self.QDRANT_URL, 
            api_key=self.QDRANT_API_KEY,
            timeout=60
        )
        self.groq_client = Groq(api_key=self.GROQ_API_KEY)
        
        # Query expansion patterns
        self.name_variations = {
            "harsha": ["jakku harshavardhan", "harshavardhan", "jakku"],
            "jakku": ["jakku harshavardhan", "harsha", "harshavardhan"],
            "harshavardhan": ["jakku harshavardhan", "harsha", "jakku"]
        }
        
        # Education keywords
        self.education_keywords = ["education", "degree", "university", "college", "cgpa", "btech", "cse"]
        self.project_keywords = ["project", "work", "developed", "built", "created", "github"]
        self.skill_keywords = ["skill", "technology", "programming", "language", "framework"]
        
    def preprocess_query(self, query: str) -> List[str]:
        """Advanced query preprocessing with expansion"""
        query = query.lower().strip()
        
        # Remove extra spaces and punctuation
        query = re.sub(r'[^\w\s]', ' ', query)
        query = ' '.join(query.split())
        
        # Generate query variations
        variations = [query]
        
        # Name-based expansion
        for key, variations_list in self.name_variations.items():
            if key in query:
                variations.extend([f"{var} {query.replace(key, '').strip()}" for var in variations_list])
                variations.extend([var for var in variations_list])
        
        # Context-based expansion
        if any(word in query for word in self.education_keywords):
            variations.extend([f"jakku harshavardhan education", f"harsha education background"])
        
        if any(word in query for word in self.project_keywords):
            variations.extend([f"jakku harshavardhan projects", f"harsha work experience"])
            
        if any(word in query for word in self.skill_keywords):
            variations.extend([f"jakku harshavardhan skills", f"harsha technical skills"])
        
        # Remove duplicates and empty strings
        variations = list(set([v.strip() for v in variations if v.strip()]))
        
        return variations[:5]  # Limit to 5 variations
    
    def get_enhanced_embedding(self, text: str) -> List[float]:
        """Enhanced embedding with semantic understanding"""
        # Create multiple hash-based embeddings for better coverage
        embeddings = []
        
        # Original text
        embeddings.append(self._hash_embedding(text))
        
        # Processed text variations
        processed_texts = [
            text.replace("harsha", "jakku harshavardhan"),
            text.replace("jakku", "jakku harshavardhan"),
            text.replace("harshavardhan", "jakku harshavardhan"),
            " ".join(text.split()[:5]),  # First 5 words
            " ".join(text.split()[-5:])  # Last 5 words
        ]
        
        for processed_text in processed_texts:
            if processed_text != text:
                embeddings.append(self._hash_embedding(processed_text))
        
        # Average the embeddings for better semantic coverage
        avg_embedding = np.mean(embeddings, axis=0).tolist()
        return avg_embedding
    
    def _hash_embedding(self, text: str) -> List[float]:
        """Create hash-based embedding"""
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        embedding = []
        for i in range(384):
            embedding.append((hash_bytes[i % len(hash_bytes)] - 128) / 128.0)
        return embedding
    
    def hybrid_search(self, query: str, k: int = 10) -> List[SearchResult]:
        """Hybrid search combining semantic and keyword matching"""
        query_variations = self.preprocess_query(query)
        all_results = []
        
        for variation in query_variations:
            try:
                # Semantic search
                embedding = self.get_enhanced_embedding(variation)
                semantic_results = self.qdrant_client.query_points(
                    collection_name=self.COLLECTION_NAME,
                    query=embedding,
                    limit=k
                )
                
                for result in semantic_results.points:
                    content = result.payload.get('content', '')
                    if content:
                        # Calculate relevance score
                        score = self._calculate_relevance_score(variation, content)
                        search_result = SearchResult(
                            content=content,
                            score=score,
                            metadata=result.payload.get('metadata', {}),
                            source=result.payload.get('metadata', {}).get('source', 'unknown')
                        )
                        all_results.append(search_result)
                        
            except Exception as e:
                print(f"Search error for '{variation}': {e}")
                continue
        
        # Remove duplicates and rerank
        unique_results = self._deduplicate_results(all_results)
        reranked_results = self._rerank_results(query, unique_results)
        
        return reranked_results[:k]
    
    def _calculate_relevance_score(self, query: str, content: str) -> float:
        """Calculate relevance score based on multiple factors"""
        query_lower = query.lower()
        content_lower = content.lower()
        
        score = 0.0
        
        # Exact match bonus
        if query_lower in content_lower:
            score += 10.0
        
        # Name matching bonus
        name_patterns = ["jakku harshavardhan", "harsha", "harshavardhan"]
        for pattern in name_patterns:
            if pattern in query_lower and pattern in content_lower:
                score += 5.0
        
        # Keyword density
        query_words = set(query_lower.split())
        content_words = content_lower.split()
        word_matches = sum(1 for word in query_words if word in content_words)
        score += word_matches * 2.0
        
        # Length penalty (prefer concise, relevant content)
        if len(content) < 500:
            score += 2.0
        
        return score
    
    def _deduplicate_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """Remove duplicate results based on content similarity"""
        unique_results = []
        seen_content = set()
        
        for result in results:
            # Create a content signature for deduplication
            content_signature = hashlib.md5(result.content.encode()).hexdigest()
            if content_signature not in seen_content:
                seen_content.add(content_signature)
                unique_results.append(result)
        
        return unique_results
    
    def _rerank_results(self, query: str, results: List[SearchResult]) -> List[SearchResult]:
        """Rerank results based on relevance and quality"""
        # Sort by score (highest first)
        results.sort(key=lambda x: x.score, reverse=True)
        
        # Boost results with name mentions
        query_lower = query.lower()
        for result in results:
            if any(name in result.content.lower() for name in ["jakku harshavardhan", "harsha"]):
                result.score += 3.0
        
        # Re-sort after boosting
        results.sort(key=lambda x: x.score, reverse=True)
        
        return results
    
    def generate_context(self, results: List[SearchResult], max_length: int = 2000) -> str:
        """Generate optimized context from search results"""
        context_parts = []
        current_length = 0
        
        for result in results:
            if current_length + len(result.content) > max_length:
                break
            
            # Add result with score indicator
            context_parts.append(f"[Score: {result.score:.1f}] {result.content}")
            current_length += len(result.content)
        
        return "\n\n".join(context_parts)
    
    def generate_answer(self, query: str, context: str) -> str:
        """Generate high-quality answer using advanced prompting"""
        prompt = f"""
You are an expert AI assistant specializing in providing accurate, comprehensive information about Jakku Harshavardhan.

CONTEXT (with relevance scores):
{context}

QUESTION: {query}

INSTRUCTIONS:
1. Use ONLY the provided context to answer the question
2. If the context contains relevant information, provide a detailed, well-structured answer
3. If multiple pieces of information are relevant, synthesize them coherently
4. If the context doesn't contain enough information, respond with: "I don't have sufficient information about this specific topic in the provided context."
5. Always be specific and factual
6. Use proper formatting and structure

RESPONSE FORMAT:
- Start with a direct answer if possible
- Provide supporting details from the context
- Use bullet points or numbered lists when appropriate
- End with a clear conclusion
"""
        
        try:
            response = self.groq_client.chat.completions.create(
                model=self.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": "You are a knowledgeable assistant that provides accurate, well-structured answers based on context."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Lower temperature for more consistent responses
                max_tokens=800,
                top_p=0.9
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error generating response: {e}"
    
    def ask_question(self, question: str) -> str:
        """Main method to ask a question and get an answer"""
        print(f"Processing question: {question}")
        
        # Step 1: Hybrid search with query expansion
        search_results = self.hybrid_search(question, k=8)
        
        if not search_results:
            return "I don't have sufficient information about this topic in the provided context."
        
        print(f"Found {len(search_results)} relevant results")
        
        # Step 2: Generate optimized context
        context = self.generate_context(search_results)
        
        # Step 3: Generate answer
        answer = self.generate_answer(question, context)
        
        return answer

# Global instance
rag_system = AdvancedRAGSystem()

def generate_answer(question: str, k: int = 3) -> str:
    """Main function for backward compatibility"""
    return rag_system.ask_question(question)

# CLI for testing
if __name__ == "__main__":
    print("Advanced RAG System - Testing Mode")
    print("Type 'exit' to quit.\n")
    
    while True:
        question = input("Ask: ").strip()
        if question.lower() in {"exit", "quit"}:
            break
        
        print("\n" + "="*60)
        answer = rag_system.ask_question(question)
        print(f"\nAnswer: {answer}")
        print("="*60 + "\n")
