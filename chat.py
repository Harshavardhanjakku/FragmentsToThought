#!/usr/bin/env python3
"""
Simple CLI interface for the Advanced RAG System
"""

from rag_system import rag_system

def main():
    print("Advanced RAG System - CLI Interface")
    print("Type 'exit' to quit.\n")
    
    while True:
        question = input("Ask: ").strip()
        if question.lower() in {"exit", "quit"}:
            break
        
        print("\n" + "="*60)
        answer = rag_system.ask_question(question)
        print(f"\nAnswer: {answer}")
        print("="*60 + "\n")

if __name__ == "__main__":
    main()
