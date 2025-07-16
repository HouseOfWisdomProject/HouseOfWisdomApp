# from functools import wraps
import os
from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, auth, firestore
from firebase_admin import exceptions as firebase_exceptions # Import Firebase specific exceptions

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

# verify_token decorator ---


# require_roles Decorator ---


# --- Flask Routes for User Account System (F1) ---

@app.route('/')
def home():
    return "Welcome to the House of Wisdom Tutoring App Backend!"

# must update register_user Function ---
@app.route('/register', methods=['POST'])
def register_user():
    """
    Handles user registration for Student, Tutor, Staff, Parent accounts.
    Expects JSON with 'email', 'password', and 'role'.
    Implements Registration, Authentication, and Role-based access control (F1).
    """
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    # Default role is 'student' if not provided
    role = data.get('role', 'student')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    try:
        # Create user in Firebase Authentication
        user = auth_service.create_user( # Changed auth.create_user to auth_service.create_user
            email=email,
            password=password,
            email_verified=False, # Can implement email verification later
            disabled=False
        )
        # Set custom claims for role-based access control (F1)
        # This is how roles like Student, Tutor, Staff, Parent are managed for access
        auth_service.set_custom_user_claims(user.uid, {'role': role})
        print(f"User {user.uid} created with role: {role}")

        # Store user data in Firestore for profile management and initial schema
        # This aligns with storing login info for different users
        # And supports creation of tutor profiles by admin
        user_ref = db.collection('users').document(user.uid)
        user_ref.set({
            'email': email,
            'role': role, # Store role in Firestore document for easy querying/display
            'created_at': firestore.SERVER_TIMESTAMP,
            'profile': { # Initial profile fields, to be expanded as per Tutor Profile (F33)
                'name': '',
                'pronouns': '',
                'description': ''
            }
        })
        print(f"User profile created in Firestore for {user.uid}")

        return jsonify({
            "message": "User registered successfully",
            "uid": user.uid,
            "role": role
        }), 201
    # Specific Firebase Auth errors can be caught for more granular responses
    except auth.EmailAlreadyExistsError:
        return jsonify({"error": "Email address already in use"}), 409 # Conflict status code
    except firebase_exceptions.FirebaseError as e: # Catch other Firebase errors
        return jsonify({"error": f"Firebase error: {e}"}), 500
    except Exception as e: # Catch any other unexpected errors
        return jsonify({"error": str(e)}), 500

# must update get_user_profile Endpoint ---
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

# must update update_user_profile Endpoint ---
@app.route('/update_profile/<uid>', methods=['PUT'])
def update_user_profile(uid):
    """
    Updates a user's profile in Firestore.
    This would be used by tutors to edit their profile.
    Requires authentication and authorization (e.g., verify ID Token to ensure user is editing their own profile or is an admin).
    """
    # In production, verify the ID token from the request header (e.g., 'Authorization: Bearer <ID_TOKEN>')
    # and check if `request.auth.uid == uid` or if the user has the 'admin' role.

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided for update"}), 400

    user_ref = db.collection('users').document(uid)
    try:
        # Construct update_data for specific fields within the 'profile' map
        update_data = {}
        if 'name' in data:
            update_data['profile.name'] = data['name'] # Update nested field
        if 'pronouns' in data:
            update_data['profile.pronouns'] = data['pronouns']
        if 'description' in data:
            update_data['profile.description'] = data['description']
        # Add other profile fields here as needed (e.g., 'picture_url' for Tutor Profile F33)
        if 'google_meets_link' in data: # Example for Online Tutoring (F6)
            update_data['google_meets_link'] = data['google_meets_link']
            # This should ideally only be updatable by an Admin or the Tutor themselves

        # If the 'role' is intended to be updated via this endpoint (e.g., by an Admin),
        # you would need to use auth_service.set_custom_user_claims() as well,
        # and ensure proper authorization for role changes.
        # Example: if 'role' in data and current_user_is_admin:
        #    auth_service.set_custom_user_claims(uid, {'role': data['role']})
        #    update_data['role'] = data['role'] # Also update Firestore for consistency

        if not update_data:
            return jsonify({"message": "No valid profile fields to update"}), 200

        user_ref.update(update_data) # Use .update() for partial updates
        return jsonify({"message": f"Profile for {uid} updated successfully"}), 200
    except firebase_exceptions.FirebaseError as e:
        return jsonify({"error": f"Firebase error during update: {e}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- Running the Flask App ---
if __name__ == '__main__':
    # To run locally during development:
    app.run(debug=True, port=5000)
    # For production deployment on PythonAnywhere, you'll use a WSGI server like Gunicorn or uWSGI
    # (e.g., from your PythonAnywhere web app settings, configure your WSGI file to point to 'app').

# powershell terminal intstructions: tab 1 for running code (python app.py), tab 2 for testing
