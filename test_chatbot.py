#!/usr/bin/env python3
"""
Test the Qdrant-powered chatbot
"""

from groqchat import generate_answer

def test_chatbot():
    print("Testing Qdrant-powered chatbot...")
    
    test_questions = [
        "Tell me about Jakku Harshavardhan",
        "Who is Harsha?",
        "What is this about?",
        "Hello"
    ]
    
    for question in test_questions:
        print(f"\nQuestion: {question}")
        print("-" * 50)
        answer = generate_answer(question)
        print(f"Answer: {answer}")
        print("-" * 50)

if __name__ == "__main__":
    test_chatbot()
