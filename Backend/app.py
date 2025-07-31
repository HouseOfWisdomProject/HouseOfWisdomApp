import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import firebase_admin
import requests
import smtplib
import ssl
from email.message import EmailMessage
from firebase_admin import credentials, auth, firestore
from firebase_admin import exceptions as firebase_exceptions # Import Firebase specific exceptions
from locations import locations #list of locations
from clock_in_out import get_location_roster, clock_in, clock_out #import clock-in/out functions
from google_sheets import update_spreadsheet #import Google Sheets update function
# Load environment variables from .env file
load_dotenv() # Call this early in your script 
FIREBASE_API_KEY = os.getenv('FIREBASE_API_KEY') # Get the API key from the environment variable 

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
        elif role == 'seniorProjectManager':
            user_data.update({
                'tutoringLocation': [],
            })
        elif role == 'juniorProjectManager':
            user_data.update({
                'tutoringLocation': [],
            })
        elif role == 'admin':
            user_data.update({
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

@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    """
    Handles a password reset request.
    Generates a password reset link and sends it to the user's email.
    """
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({"error": "Email is required"}), 400

    try:
        # Generate password reset link
        link = auth.generate_password_reset_link(email)

        # --- Send Email ---
        # For this to work, you need to configure an email sender.
        # This example uses Gmail's SMTP server.
        # IMPORTANT: For security, use an "App Password" for your Gmail account, not your regular password.
        # You can generate an App Password here: https://myaccount.google.com/apppasswords
        email_sender = 'ayaank1532@gmail.com'  # Replace with your email
        email_password = 'voye yncj ftiq neav'  # Replace with your App Password
        email_receiver = email

        subject = "Password Reset for House of Wisdom App"
        body = f"""
        Hello,

        You requested a password reset for your House of Wisdom account.
        Please click the link below to reset your password:
        {link}

        If you did not request this, please ignore this email.

        Thank you,
        The House of Wisdom Team
        """

        em = EmailMessage()
        em['From'] = email_sender
        em['To'] = email_receiver
        em['Subject'] = subject
        em.set_content(body)

        # Add SSL (layer of security)
        context = ssl.create_default_context()

        # Log in and send the email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.sendmail(email_sender, email_receiver, em.as_string())

        return jsonify({"message": "A password reset link has been sent to your email."}), 200

    except auth.UserNotFoundError:
        # It's good practice not to reveal if an email is registered or not for security reasons.
        return jsonify({"message": "If your email is registered, you will receive a password reset link."}), 200
    except Exception as e:
        # Log the error for debugging, but don't expose it to the user.
        print(f"Error in forgot_password: {e}")
        return jsonify({"error": "An error occurred while trying to reset the password. Please try again later."}), 500
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

    # CRITICAL: Check if FIREBASE_API_KEY is available
   if not FIREBASE_API_KEY:
       return jsonify({"error": "Firebase Web API Key is not configured on the server."}), 500
       
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
        
        if 'tutoringLocation' in data:
            new_locations =  data['tutoringLocation']
            #Validate locations against the predefned list
            if isinstance(new_locations, list) and all(loc in locations for loc in new_locations):
                update_data['tutoringLocation'] = new_locations
            else:
                 return jsonify({"error": "Invalid data provided for tutoringLocation. Must be a list of valid locations."}), 400
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

#Additions for the clock-in/out system

#@app.route('/roster/<location>', methods=['GET']): This new route will handle requests for the list of
#staff members at a specific location. It will call the get_location_roster function from the clock_in_out.py 
#file and return the list as a JSON response.
@app.route('/roster/<location>', methods = ['GET'])
def get_roster (location):
    try: 
        roster = get_location_roster(location)
        return jsonify(roster), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#@app.route('/clock_in', methods=['POST']): This route will handle clock-in requests. It will receive the user 
#ID and location from the request body, call the clock_in function from clock_in_out.py, and then trigger the 
#update_spreadsheet function in google_sheets.py to log the event in the appropriate Google Sheet.
@app.route('/clock_in', methods = ['POST'])
def handle_clock_in():
    data = request.get_json()
    user_id = data.get('user_id')
    location = data.get('location')
    role = data.get('role')

    if not user_id or not location:
        return jsonify({"error", "user id and location are required"}), 400
        
    try:
        event = clock_in(user_id, location, role)
        update_spreadsheet(location, event)
        return jsonify({"message": "Clock-in successful", "data": event}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

#@app.route('/clock_out', methods=['POST']): This route will handle clock-out requests. It will receive the 
#user ID and location from the request body, call the clock_out function, and update the corresponding Google Sheet.
@app.route('/clock_out', methods=['POST'])
def handle_clock_out():
    data = request.get.json()
    user_id = data.het('user_id')
    location = data.get('location')
    role = data.get('role')
    
    if not user_id or not location:
        return jsonify({"error","user id and location are required "}), 400
    try:
        event = clock_out(user_id, location, role)
        update_spreadsheet(location, event)
        return jsonify({"message": "Clock-out successful", "data": event}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
#@app.route('/work_hours', methods=['GET'])
#retrieves work hours for a specific user and date from Firestore.
#This route is used to fetch time-tracking data for reporting purposes.
@app.route('/work_hours', methods=['GET'])
def get_work_hours():
    user_id = request.args.get('user_id')
    date = request.args.get('date')

    if not user_id or not date:
        return jsonify({"error": "user_id and date are required"}), 400
        try:
            # Query work hours for the user on the specified date
            work_ref = db.collections('work_hours').where('user_id', '==', user_id).where('date', '==', date).get()
            work_hours = [doc.to_dict() for doc in work_ref]

            return jsonify(work_hours), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
