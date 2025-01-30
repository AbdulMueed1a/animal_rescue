# firebase.py (create this file in your app directory)
import firebase_admin
from firebase_admin import credentials

def initialize_firebase():
    cred = credentials.Certificate("../firebase-key.json")
    firebase_admin.initialize_app(cred)