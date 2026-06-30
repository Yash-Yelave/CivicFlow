import os
import sys
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

def test_firebase_connection():
    print("Loading environment variables...")
    load_dotenv()
    
    service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY")
    if not service_account_path:
        print("ERROR: FIREBASE_SERVICE_ACCOUNT_KEY not found in .env file.")
        return
        
    print(f"Checking for credentials file at: '{service_account_path}'")
    if not os.path.exists(service_account_path):
        print(f"ERROR: Credentials file not found at: '{service_account_path}'")
        return
    else:
        print("Found credentials file.")

    print("Initializing Firebase SDK...")
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred)
        print("Firebase SDK initialized successfully.")
        
        print("Connecting to Firestore...")
        db = firestore.client()
        
        # Test Firestore by trying to retrieve a collection (like tickets)
        # Even if the collection is empty, listing documents shouldn't error out.
        print("Testing Firestore read permission (fetching tickets collection)...")
        tickets_ref = db.collection("tickets").limit(1)
        docs = list(tickets_ref.stream())
        
        print(f"Read operation successful. Found {len(docs)} documents (limited to 1).")
        print("\nSUCCESS: Firebase/Firestore connection is fully operational!")
        
    except Exception as e:
        print("\nFAILURE: Firebase connection failed.")
        print(f"Error details: {str(e)}")
        
if __name__ == "__main__":
    test_firebase_connection()
