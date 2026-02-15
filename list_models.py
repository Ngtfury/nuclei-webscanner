from google import genai
import os

GEMINI_API_KEY = "AIzaSyD7diSRMs-CoNXB2zoc11b7bFbf77CdnTk"
client = genai.Client(api_key=GEMINI_API_KEY)

try:
    print("Listing models...")
    # The new SDK might specific syntax for listing models, checking docs or guessing common patterns
    # Based on migration guides, it might be client.models.list()
    for model in client.models.list():
        print(f"Model: {model.name}")
        # if "generateContent" in (model.supported_generation_methods or []):
        #      print(f"  - Supports generateContent")

except Exception as e:
    print(f"Error: {e}")
