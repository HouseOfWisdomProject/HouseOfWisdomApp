# firebase_config.py
import firebase_admin
from firebase_admin import credentials, firestore
import os

# Path to your downloaded service account key JSON file
service_account_key_path = os.path.join(os.path.dirname(__file__), 'serviceAccountKey.json')

try:
    cred = credentials.Certificate(service_account_key_path)
    firebase_admin.initialize_app(cred)
    db = firestore.client() # Initialize Firestore client
    print("Firebase Admin SDK initialized successfully.")
except Exception as e:
    print(f"Error initializing Firebase Admin SDK: {e}")
    db = None
    exit(1)