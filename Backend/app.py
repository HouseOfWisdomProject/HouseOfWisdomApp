import os
from dotlenv import load_dotenv 
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import smtplib
import ssl
from email.message import EmailMessage
from firebase_admin import auth, exceptions as firebase_exceptions
from locations import locations
from clock_in_out import get_location_roster, clock_in, clock_out
from logging_google_sheets import update_spreadsheet, generate_15_day_location_summary, cleanup_old_sheets
from firebase_config import db  
from datetime import datetime
from firebase_admin import firestore
from attendance import get_student_list, take_attendance, edit_attendance, attendance_count
from attendance_google_sheet import micro_attendance, macro_attendance
from edit_work_hours import app as edit_work_hours_app
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Application started")
logger.warning("This is a warning")
logger.error("An error occurred")

# Load environment variables from .env file
load_dotenv()
FIREBASE_API_KEY = os.getenv('FIREBASE_API_KEY')

app = Flask(__name__, static_folder='../frontend/build',static_url_path='/')
CORS(app)

# Register the routes from edit_work_hours.py
app.register_blueprint(edit_work_hours_app, url_prefix='/work_hours')

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
    firstName = data.get('firstName')
    lastName = data.get('lastName')
    role = data.get('role', 'student') # Default role is 'student'

    if not all([email, password, firstName, lastName]):
        return jsonify({"error": "Email, password, firstName, and lastName are required"}), 400

    try:
        # Create user in Firebase Authentication
        user = auth.create_user(
            email=email,
            password=password,
            display_name=f"{firstName} {lastName}" # Set display name in Auth
        )
        # Set custom claims for role-based access control
        auth.set_custom_user_claims(user.uid, {'role': role})

        # --- This section now implements your DB Schema ---
        user_data = {
            'email': email,
            'firstName': firstName,
            'lastName': lastName,
            'role': role,
            'created_at': firestore.SERVER_TIMESTAMP
        }

        if role == 'student':
            user_data.update({
                'gradeLevel': data.get('gradeLevel', None),
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
        elif role in ['seniorProjectManager', 'juniorProjectManager']:
            user_data.update({
                'tutoringLocation': [],
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
    """
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({"error": "Email is required"}), 400

    try:
        link = auth.generate_password_reset_link(email)
        
        # Email sending logic...
        email_sender = 'ayaank1532@gmail.com'
        email_password = 'voye yncj ftiq neav' # Consider using environment variables for this
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

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.sendmail(email_sender, email_receiver, em.as_string())

        return jsonify({"message": "A password reset link has been sent to your email."}), 200

    except auth.UserNotFoundError:
        return jsonify({"message": "If your email is registered, you will receive a password reset link."}), 200
    except Exception as e:
        print(f"Error in forgot_password: {e}")
        return jsonify({"error": "An error occurred while trying to reset the password."}), 500

@app.route('/login', methods=['POST'])
def login_user():
   """
   Logs in a user using email and password via Firebase Auth REST API.
   """
   data = request.get_json()
   email = data.get('email')
   password = data.get('password')

   if not email or not password:
       return jsonify({"error": "Email and password are required"}), 400

   if not FIREBASE_API_KEY:
       return jsonify({"error": "Firebase Web API Key is not configured on the server."}), 500
       
   try:
       url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
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
    """
    user_ref = db.collection('users').document(uid)
    user_doc = user_ref.get()

    if user_doc.exists:
        profile_data = user_doc.to_dict()
        if 'created_at' in profile_data and hasattr(profile_data['created_at'], 'isoformat'):
             profile_data['created_at'] = profile_data['created_at'].isoformat()
        return jsonify(profile_data), 200
    else:
        return jsonify({"error": "User profile not found"}), 404

@app.route('/update_profile/<uid>', methods=['PUT'])
def update_user_profile(uid):
    """
    Updates a user's profile in Firestore.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided for update"}), 400

    user_ref = db.collection('users').document(uid)
    try:
        update_data = {}
        
        if 'tutoringLocation' in data:
            new_locations =  data['tutoringLocation']
            if isinstance(new_locations, list) and all(loc in locations for loc in new_locations):
                update_data['tutoringLocation'] = new_locations
            else:
                 return jsonify({"error": "Invalid data for tutoringLocation."}), 400
        # Add other updatable fields here
        # ...

        if not update_data:
            return jsonify({"message": "No valid profile fields to update"}), 200

        user_ref.update(update_data)
        return jsonify({"message": f"Profile for {uid} updated successfully"}), 200
    except firebase_exceptions.FirebaseError as e:
        return jsonify({"error": f"Firebase error during update: {e}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Clock-in/out System Routes ---

@app.route('/roster/<location>', methods=['GET'])
def get_roster(location):
    try: 
        roster = get_location_roster(location)
        return jsonify(roster), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/clock_in', methods=['POST'])
def handle_clock_in():
    data = request.get_json()
    user_id = data.get('user_id')
    location = data.get('location')
    role = data.get('role')

    if not user_id or not location or not role:
        return jsonify({"error": "user_id, location, and role are required"}), 400
        
    try:
        event_data = clock_in(user_id, location, role)
        # You'll need to get the user's first/last name to pass to the sheet
        user_info = db.collection('users').document(user_id).get().to_dict()
        sheet_data = {**event_data, **user_info}
        update_spreadsheet(location, sheet_data)
        return jsonify({"message": "Clock-in successful", "data": event_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/clock_out', methods=['POST'])
def handle_clock_out():
    data = request.get_json()
    user_id = data.get('user_id')
    location = data.get('location')
    role = data.get('role')
    
    if not user_id or not location or not role:
        return jsonify({"error": "user_id, location, and role are required"}), 400
    try:
        event_data = clock_out(user_id, location, role)
        # You'll need to get the user's first/last name to pass to the sheet
        user_info = db.collection('users').document(user_id).get().to_dict()
        sheet_data = {**event_data, **user_info}
        update_spreadsheet(location, sheet_data)
        return jsonify({"message": "Clock-out successful", "data": event_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/work_hours', methods=['GET'])
def get_work_hours():
    user_id = request.args.get('user_id')
    date = request.args.get('date')

    if not user_id or not date:
        return jsonify({"error": "user_id and date are required"}), 400
    try:
        work_ref = db.collection('work_hours').where('user_id', '==', user_id).where('date', '==', date).get()
        work_hours = [doc.to_dict() for doc in work_ref]
        return jsonify(work_hours), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/work_hours/health', methods=['GET'])
def work_hours_health():
    return jsonify({"status": "Work Hours API is running"}), 200

#15 Day Summary Route
@app.route('/15_day_summary/<location>', methods = ['POST'])
def handle_15_day_summary(location):
    """ Generates a 15-day summary report for a specific location.
    """
    try:
        result = generate_15_day_location_summary(location)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error" : f"failed to generate summary for {location}: {str(e)}"}), 500
     
#Attendance Routes

#Retrieves a list of all students registered at a specific tutoring location
@app.route('/attendance/students/<location>', methods=['GET'])
def handle_get_student_list(location):
    """
    Retrieves a list of all students registered at a specific tutoring location.
    """
    try:
        students = get_student_list(location)
        return jsonify(students), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
#Handles the attendance for a student
@app.route('/attendance/take', methods=['POST'])
def handle_take_attendance():
    """
    Endpoint to record attendance for a student.
    Calls the take_attendance function.
    """
    data = request.get_json()
    location = data.get('location')
    student_id = data.get('student_id')
    status = data.get('status')

    if not all([location, student_id, status]):
        return jsonify({"error": "location, student_id, and status are required"}), 400
    
    if status not in ['present', 'absent']:
        return jsonify({"error": "status must be 'present' or 'absent'"}), 400

    try:
        # This will call the function from attendance.py
        result = take_attendance(location, student_id, status)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
#Handles the editing of a students attendance
@app.route('/attendance/edit', methods=['PUT'])
def handle_edit_attendance():
    """
    Endpoint to edit a student's attendance record."""
    data = request.get_json()
    location = data.get('location')
    student_id = data.get('student_id')
    status = data.get('status')

    if not all ([location, student_id, status]):
        return jsonify({"error": "location, student_id, and status are required"}), 400
    if status not in ['present', 'absent']:
        return jsonify({"error" : "status must be 'present' or absent'"}), 400
    try:
        result = edit_attendance(location, student_id, status)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
#Handles the count of present students at a location 
@app.route('/attendance/count/<location>', methods=['GET'])
def handle_attendance_count(location):   
    """
    Endpoint to get the count of present students at a location for the current day.
    Calls the attendance_count function.
    """
    try:
        #This will call the function from attendance.py
        count = attendance_count(location)
        return jsonify(count), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500  
    
# --- Admin Routes ---
from payroll_validation import handle_payroll_approval 

@app.route('/payroll/approval', methods=['POST'])
def admin_payroll_approve(): 
    """
    Endpoint to approve payroll for a specific location and pay period.
    """
    data = request.get_json()
    location = data.get('location')
    if not location:
        return jsonify({"error": "location is required"}), 400
    result = handle_payroll_approval(location)
    return jsonify(result), 200 if result.get("status") == "success" else 500

from payroll_validation import handle_payroll_approval, send_final_approval_email

@app.route('/payroll/send_final_email', methods=['POST'])
def trigger_final_payroll_email():
    """
    Manually triggers the final payroll email to all admins after all locations are approved.
    """
    try:
        send_final_approval_email()
        return jsonify({"message": "Final payroll email sent."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/payroll/approval/summary', methods=['GET'])
def admin_payroll_approval_summary():
    """
    Endpoint to get a summary of payroll approvals for the current pay period.
    """
    try:
        summaries = []
        for loc in locations:
            summary = db.collection('payroll_approvals').document(f"{loc}_{datetime.now().strftime('%Y-%m-%d')}").get()
            if summary.exists:
                summaries.append({loc: summary.to_dict()})
        return jsonify(summaries), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

from logging_google_sheets import cleanup_old_sheets
@app.route('/payroll/cleanup', methods=['POST'])
def admin_cleanup_sheets():
    """
    Endpoint to clean up old Google Sheets for payroll.
    """
    try:
        cleanup_old_sheets()
        return jsonify({"message": "Old sheets cleaned up successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500 

# --- Running the Flask App ---
if __name__ == '__main__':
    app.run(debug=True, port=5000)

@app.route('/attendance/micro', methods=['POST'])
def handle_micro_attendance():
    """
    Endpoint to trigger daily attendance logging into Google Sheets for a given location.
    Expects a JSON body with 'google_sheet_name' and 'location'.
    """
    data = request.get_json()
    google_sheet_name = data.get('google_sheet_name')
    location = data.get('location')

    if not google_sheet_name or not location:
        return jsonify({"error": "google_sheet_name and location are required"}), 400

    try:
        micro_attendance(google_sheet_name, location)
        return jsonify({"message": f"Micro attendance logged successfully for {location}."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/attendance/macro', methods=['POST'])
def handle_macro_attendance():
    """
    Endpoint to trigger monthly attendance summary logging.
    Only works if today is the 1st of the month.
    """
    try:
        today = datetime.now()
        if today.day != 1:
            return jsonify({"message": "Macro attendance reports are only generated on the 1st day of each month."}), 400
        
        macro_attendance()
        return jsonify({"message": "Macro attendance report generated successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Additional Routes
@app.route('/users', methods=['GET'])
def list_users():
    """
    Retrieves all users from the Firestore 'users' collection.
    Returns a list of user profiles including their UID.
    Intended for admin use only.
    """
    try:
        users_ref = db.collection('users').stream()
        users = [{**doc.to_dict(), "uid": doc.id} for doc in users_ref]
        return jsonify(users), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/user/<uid>', methods=['DELETE'])
def delete_user(uid):
    """
    Deletes a user from Firebase Authentication and Firestore by UID.
    Intended for admin control of user lifecycle.
    """
    try:
        auth.delete_user(uid)
        db.collection('users').document(uid).delete()
        return jsonify({"message": f"User {uid} deleted."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/analytics/clockins_today', methods=['GET'])
def clockins_today():
    """
    Returns the number of users who clocked in today across all locations.
    Useful for internal analytics or dashboard metrics.
    """
    try:
        today = datetime.now().date().isoformat()
        shifts = db.collection('shifts').where('event', '==', 'clock-in').stream()
        today_count = sum(1 for s in shifts if s.to_dict().get('timestamp', '').startswith(today))
        return jsonify({"clock_ins_today": today_count}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

