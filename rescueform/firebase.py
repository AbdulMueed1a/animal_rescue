# rescueform/firebase.py
import firebase_admin
from firebase_admin import credentials

def initialize_firebase():
    try:
        cred = credentials.Certificate("firebase-key.json")  # Update path
        firebase_admin.initialize_app(cred)
        print("✅ Firebase initialized successfully")
    except Exception as e:
        print(f"❌ Firebase initialization failed: {str(e)}")