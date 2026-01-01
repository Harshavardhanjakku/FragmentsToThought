from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

def test_groq():
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        print("❌ GROQ_API_KEY not found in .env")
        return

    print("✅ GROQ_API_KEY loaded")

    client = Groq(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello and confirm Groq is working."}
            ],
            max_tokens=50
        )

        print("\n🎉 GROQ RESPONSE:")
        print(response.choices[0].message.content)

    except Exception as e:
        print("\n❌ GROQ API ERROR:")
        print(e)

if __name__ == "__main__":
    test_groq()
