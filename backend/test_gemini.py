import os
from dotenv import load_dotenv
import google.generativeai as genai

def test_gemini_connection():
    print("Loading environment variables...")
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not found in .env file.")
        return
        
    # Mask key for secure logging
    masked_key = f"{api_key[:6]}...{api_key[-4:]}"
    print(f"Found GEMINI_API_KEY: {masked_key}")
    
    print("Initializing Gemini SDK...")
    genai.configure(api_key=api_key)
    
    print("Testing connection to gemini-1.5-flash...")
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content("Hello! Please reply with a short 'Hello, I am ready!' to confirm you are online.")
        
        print("\n--- GEMINI RESPONSE ---")
        print(response.text.strip())
        print("-----------------------")
        print("SUCCESS: Gemini API is fully operational!")
        
    except Exception as e:
        print("\nFAILURE: Gemini API call failed.")
        print(f"Error details: {str(e)}")

if __name__ == "__main__":
    test_gemini_connection()
