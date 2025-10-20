#!/usr/bin/env python3
"""
Test the optimized RAG system
"""

from advanced_rag import rag_system

def test_optimized_rag():
    print("Testing Optimized RAG System")
    print("="*50)
    
    test_questions = [
        "Who is Harsha?",
        "What is Harsha education?",
        "What projects has Harsha worked on?",
        "Tell me about Jakku Harshavardhan",
        "What is Harsha CGPA?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{i}. Question: {question}")
        print("-" * 40)
        answer = rag_system.ask_question(question)
        print(f"Answer: {answer}")
        print("-" * 40)

if __name__ == "__main__":
    test_optimized_rag()
