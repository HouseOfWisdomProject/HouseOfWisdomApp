import os
from flask import Flask, request, jsonify
import firebase_admin
import requests
from firebase_admin import credentials, auth, firestore
from firebase_admin import exceptions as firebase_exceptions # Import Firebase specific exceptions
FIREBASE_API_KEY = 'AIzaSyCii0tWtKfl1AfuYicA5Pf986jlCYDJZb4'  # Get this from Firebase Console > Project Settings > General


app = Flask(__name__)


# --- Firebase Initialization ---
# Path to your downloaded service account key JSON file
# This file contains your project's credentials. Keep it secure!
# For production deployment (e.g., on PythonAnywhere), store this path or the key content
# in environment variables, not directly in code.
service_account_key_path = os.path.join(os.path.dirname(__file__), 'serviceAccountKey.json')


try:
   cred = credentials.Certificate(service_account_key_path)
   firebase_admin.initialize_app(cred)
   db = firestore.client() # Initialize Firestore client
   auth_service = auth # Assign auth module to a variable for consistent use
   print("Firebase Admin SDK initialized successfully for the app.")
except Exception as e:
   print(f"Error initializing Firebase Admin SDK for the app: {e}")
   # In a real app, you might use a logging library here.
   # If Firebase initialization fails, the app cannot function.
   exit(1) # Exit if Firebase fails to initialize


# --- Flask Routes for User Account System (F1) ---


@app.route('/')
def home():
   return "Welcome to the House of Wisdom Tutoring App Backend!"


@app.route('/register', methods=['POST'])
def register_user():
    """
    Handles user registration and creates a Firestore document
    that matches the User Account DB Schema.
    """
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    # Get schema fields from the request
    firstName = data.get('firstName')
    lastName = data.get('lastName')
    role = data.get('role', 'student') # Default role is 'student'

    if not all([email, password, firstName, lastName]):
        return jsonify({"error": "Email, password, firstName, and lastName are required"}), 400

    try:
        # Create user in Firebase Authentication
        user = auth_service.create_user(
            email=email,
            password=password,
            display_name=f"{firstName} {lastName}" # Set display name in Auth
        )
        # Set custom claims for role-based access control
        auth_service.set_custom_user_claims(user.uid, {'role': role})

        # --- This section now implements your DB Schema ---
        # Start with the base user fields shared by all roles
        user_data = {
            'email': email,
            'firstName': firstName,
            'lastName': lastName,
            'role': role,
            'created_at': firestore.SERVER_TIMESTAMP
        }

        # Add role-specific fields based on the schema
        if role == 'student':
            user_data.update({
                'gradeLevel': data.get('gradeLevel', None), # Expect gradeLevel from client
                'parentContact': data.get('parentContact', ''),
                'tutoringLocation': [],
                'topics': []
            })
        elif role == 'tutor':
            user_data.update({
                'googleMeetsLink': '',
                'tutoringLocation': [],
                'topics': []
            })
        elif role == 'staff':
            user_data.update({
                'tutoringLocation': [],
                'permissions': []
            })
        elif role == 'admin':
            user_data.update({
                'permissions': []
            })

        # Create the document in Firestore
        db.collection('users').document(user.uid).set(user_data)

        return jsonify({
            "message": "User registered successfully",
            "uid": user.uid,
            "role": role
        }), 201

    except auth.EmailAlreadyExistsError:
        return jsonify({"error": "Email address already in use"}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 500






@app.route('/login', methods=['POST'])
def login_user():
   """
   Logs in a user using email and password via Firebase Auth REST API.
   Returns Firebase ID token if login is successful.
   """
   data = request.get_json()
   email = data.get('email')
   password = data.get('password')


   if not email or not password:
       return jsonify({"error": "Email and password are required"}), 400


   try:
       # Call Firebase REST API to verify password
       url = url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
       payload = {
           "email": email,
           "password": password,
           "returnSecureToken": True
       }
       response = requests.post(url, json=payload)
       if response.status_code != 200:
           return jsonify({"error": "Invalid email or password"}), 401


       res_data = response.json()
       return jsonify({
           "message": "Login successful",
           "idToken": res_data.get("idToken"),
           "refreshToken": res_data.get("refreshToken"),
           "expiresIn": res_data.get("expiresIn"),
           "uid": res_data.get("localId")
       }), 200


   except Exception as e:
       return jsonify({"error": str(e)}), 500




@app.route('/user_profile/<uid>', methods=['GET'])
def get_user_profile(uid):
   """
   Retrieves a user's profile information from Firestore.
   This can be used for 'Tutor Profile' or basic student profiles.
   Requires authentication and authorization (via Firebase ID Token verification on backend, or Firebase Security Rules for direct client access).
   """
   # In a real app, you'd verify the ID token from the request header (e.g., 'Authorization: Bearer <ID_TOKEN>')
   # to ensure the requester is authorized to view this profile (e.g., own profile or admin viewing).
   # For simplicity, this example fetches data directly.
   # Firebase Security Rules will be crucial for actual access control on the client side.


   user_ref = db.collection('users').document(uid)
   user_doc = user_ref.get()


   if user_doc.exists:
       profile_data = user_doc.to_dict()
       # Remove created_at if not needed by client for display, or format it
       if 'created_at' in profile_data and hasattr(profile_data['created_at'], 'isoformat'):
            profile_data['created_at'] = profile_data['created_at'].isoformat() # Convert Timestamp to string
       return jsonify(profile_data), 200
   else:
       return jsonify({"error": "User profile not found"}), 404


@app.route('/update_profile/<uid>', methods=['PUT'])
def update_user_profile(uid):
    """
    Updates a user's profile in Firestore according to the DB schema.
    This is flexible and updates any valid top-level field provided.
    Requires authentication and authorization.
    """
    # In production, you must verify the ID token from the request header
    # to ensure the user is authorized to make this change.

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided for update"}), 400

    user_ref = db.collection('users').document(uid)

    # For security, prevent users from changing their role or email via this endpoint.
    # These should be handled by a separate, admin-only function if needed.
    data.pop('role', None)
    data.pop('email', None)

    if not data:
        return jsonify({"error": "No valid fields to update. Note: 'role' and 'email' cannot be changed here."}), 400

    try:
        # This now directly updates any top-level fields sent in the request.
        # It's now aligned with your schema.
        user_ref.update(data)
        return jsonify({"message": f"Profile for {uid} updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500




# --- Running the Flask App ---
if __name__ == '__main__':
   # To run locally during development:
   app.run(debug=True, port=5000)
   # For production deployment on PythonAnywhere, you'll use a WSGI server like Gunicorn or uWSGI
   # (e.g., from your PythonAnywhere web app settings, configure your WSGI file to point to 'app').
