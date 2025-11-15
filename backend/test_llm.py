"""Test LLM service."""
from app.services.llm_service import llm_service

# Sample text
title = "Python Programming Language"
content = """Python is a high-level, general-purpose programming language. 
Its design philosophy emphasizes code readability with the use of significant indentation. 
Python is dynamically type-checked and garbage-collected. 
It supports multiple programming paradigms, including structured, object-oriented and functional programming.
Guido van Rossum began working on Python in the late 1980s as a successor to the ABC programming language.
Python 2.0 was released in 2000. Python 3.0, released in 2008, was a major revision not completely backward-compatible with earlier versions."""

print("Testing LLM Service...")
print("\n1. Testing Summary Generation...")
try:
    summary = llm_service.generate_summary(title, content)
    print(f"Summary: {summary}")
except Exception as e:
    print(f"Error: {e}")

print("\n2. Testing Entity Extraction...")
try:
    entities = llm_service.extract_entities(title, content)
    print(f"Entities: {entities}")
except Exception as e:
    print(f"Error: {e}")

print("\n3. Testing Quiz Generation (2 questions)...")
try:
    quiz = llm_service.generate_quiz(title, content, num_questions=2)
    print(f"Generated {len(quiz)} questions")
    for i, q in enumerate(quiz, 1):
        print(f"\nQ{i}: {q['question']}")
        print(f"Answer: {q['answer']} - {q['difficulty']}")
except Exception as e:
    print(f"Error: {e}")

print("\n✅ LLM Service Test Complete!")
