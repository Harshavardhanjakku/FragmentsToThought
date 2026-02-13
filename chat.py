#!/usr/bin/env python3
"""
Simple CLI interface for the Advanced RAG System.
Uses the production RAG defined in rag_system.py.
"""

from rag_system import rag


def main() -> None:
    print("Advanced RAG System - CLI Interface (Qdrant + Groq)")
    print("Type 'exit' to quit.\n")

    try:
        while True:
            question = input("Ask: ").strip()
            if question.lower() in {"exit", "quit"}:
                break
            if not question:
                print("Please enter a question (or type 'exit' to quit).")
                continue

            print("\n" + "=" * 60)
            answer = rag.ask(question)
            print(f"\nAnswer: {answer}")
            print("=" * 60 + "\n")
    except KeyboardInterrupt:
        print("\nExiting Advanced RAG CLI.")


if __name__ == "__main__":
    main()
