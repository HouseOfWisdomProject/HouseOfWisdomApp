# payroll_validation.py

# This file contains the backend logic for the payroll validation and approval process.
# When a Senior Project Manager (Senior PM) validates the payroll for their location,
# this script triggers a series of actions to generate reports, send notifications,
# and consolidate payroll data from all locations.

# --- Imports ---
# Standard library imports for email, CSV creation, and date/time handling.
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import csv
import io
from datetime import datetime, timedelta

# Firebase and Google Cloud imports for database interaction.
from firebase_admin import firestore
from firebase_config import db # Assumes 'db' is the initialized Firestore client from your config.

# Imports from other project files.
from locations import locations # List of all tutoring locations.
# We will need a function similar to generate_15_day_location_summary from logging_google_sheets.py
# For this example, we'll assume a helper function exists to fetch this data.

# --- Constants ---
# Email configuration for sending notifications.
# It's recommended to store these in environment variables for security.
SENDER_EMAIL = "your_email@example.com"
SENDER_PASSWORD = "your_email_password"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465

# --- Main Functions ---
def handle_payroll_approval(location):
    """
    Main function triggered when a Senior PM clicks the 'Approve' button for their location.

    This function will:
    1. Generate the 15-day payroll summary for the specified location.
    2. Create a CSV file from that summary.
    3. Email the CSV to all admin users.
    4. Record the approval status for the location.
    5. Check if all locations have been approved and, if so, trigger the final email.
    """
    print(f"Starting payroll approval process for {location}...")
    try:
        # 1. Generate the 15-day payroll summary CSV data in memory.
        csv_data, start_date, end_date = generate_payroll_data_for_location(location)
        if not csv_data or len(csv_data) <= 1: # Header only or empty
            print(f"No payroll data found for {location}. Aborting.")
            return {"status": "error", "message": f"No payroll data to approve for {location}."}

        # Create a filename for the CSV attachment using the pay period dates.
        csv_filename = f"{location}_payroll_{start_date.strftime('%Y-%m-%d')}_to_{end_date.strftime('%Y-%m-%d')}.csv"

        # 2. Fetch the list of all admin users from Firestore.
        admin_emails = get_admin_emails()
        if not admin_emails:
            print("No admin emails found. Cannot send approval email.")
            return {"status": "error", "message": "Could not find any admin users to notify."}

        # 3. Send the location-specific payroll CSV to all admins.
        send_location_approval_email(admin_emails, location, csv_data, csv_filename)

        # 4. Record that this location's payroll has been approved for the current pay period.
        record_location_approval(location)

        # 5. Check if all locations have now been approved.
        if check_all_locations_approved():
            send_final_approval_email()

        print(f"Payroll approval process for {location} completed successfully.")
        return {"status": "success", "message": f"Payroll for {location} approved and email sent."}

    except Exception as e:
        print(f"An error occurred during payroll approval for {location}: {e}")
        return {"status": "error", "message": str(e)}

# --- Helper Functions ---

def generate_payroll_data_for_location(location):
    """
    Fetches and calculates the 15-day payroll data for a given location.
    This function replicates the core logic of `generate_15_day_location_summary`.
    """
    today = datetime.now().date()
    # This logic now exactly mirrors the logic in logging_google_sheets.py
    # to ensure consistency between sheet names and CSV names.
    if today.day > 15:
        start_date = today.replace(day=16)
        # End of the current month
        end_date = (today.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    else:
        start_date = today.replace(day=1)
        end_date = today.replace(day=15)


    users_query = db.collection('users').where('tutoringLocation', 'array_contains', location).stream()
    location_users = {user.id: user.to_dict() for user in users_query}
    report_data = [['First Name', 'Last Name', 'Role', 'Total Hours']]

    for user_id, user_data in location_users.items():
        total_duration = timedelta()
        shifts_ref = db.collection('shifts').where('user_id', '==', user_id).where('location', '==', location).order_by('timestamp').stream()
        
        clock_in_time = None
        for shift in shifts_ref:
            shift_data = shift.to_dict()
            # Timestamps are stored as ISO format strings, convert them to datetime objects
            event_time = datetime.fromisoformat(shift_data.get("timestamp"))

            if not (start_date <= event_time.date() <= end_date):
                continue

            if shift_data.get("event") == 'clock-in':
                clock_in_time = event_time
            elif shift_data.get("event") == 'clock-out' and clock_in_time:
                duration = event_time - clock_in_time
                total_duration += duration
                clock_in_time = None 

        if total_duration.total_seconds() > 0:
            total_hours = round(total_duration.total_seconds() / 3600, 2)
            report_data.append([
                user_data.get('firstName', ''),
                user_data.get('lastName', ''),
                user_data.get('role', ''),
                total_hours
            ])
    return report_data, start_date, end_date

def get_admin_emails():
    """
    Queries the 'users' collection in Firestore to get the email addresses
    of all users with the role 'admin'.
    
    Returns:
        A list of email addresses (strings).
    """
    # Placeholder for Firestore query logic.
    # users_ref = db.collection('users').where('role', '==', 'admin').stream()
    # emails = [user.to_dict().get('email') for user in users_ref]
    # return emails
    try:
        users_ref = db.collection('users').where('role', '==', 'admin').stream()
        emails = [user.to_dict().get('email') for user in users_ref if user.to_dict().get('email')]
        return emails
    except Exception as e:
        print(f"Error fetching admin emails: {e}")
        return []

def send_location_approval_email(recipient_emails, location, csv_data, filename):
    """
    Composes and sends an email with the location-specific payroll CSV attached.
    """
    # Logic to create an email message using smtplib.
    # The message body would indicate which location's payroll has been approved.
    # The csv_data would be attached as a file.
    
    # Companies and sends and email with the location-specific payroll CSV attached.
    message = MIMEMultipart()
    message["From"] = SENDER_EMAIL
    message["To"] = ', '.join(recipient_emails)
    
    body = f"""
    Hello Admin Team,
    
    The payroll for the location ***{location} has been approved for your records.
    
    Regards,
    Payroll Automation System
    """
    message.attach(MIMEText(body, "plain"))

    # Attach the CSV file
    part = MIMEBase("application", "octet-stream")
    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerows(csv_data)
    part.set_payload(csv_buffer.getvalue().encode("utf-8"))
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f"attachment; filename={filename}")
    message.attach(part)

    # Send the email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(message)
    

def record_location_approval(location):
    """
    Records a document in Firestore to signify that a location's payroll
    has been approved for the current pay period.
    
    This could be a collection named 'payroll_approvals' with documents
    named after the location and pay period.
    """
    # Placeholder for Firestore write operation.
    # pay_period_id = f"{datetime.now().year}-{datetime.now().month}-{1 if datetime.now().day <= 15 else 16}"
    # approval_ref = db.collection('payroll_approvals').document(f"{location}_{pay_period_id}")
    # approval_ref.set({
    #     'location': location,
    #     'approved_at': firestore.SERVER_TIMESTAMP,
    #     'status': 'approved'
    # })
    try:
        # determine the current pay period
        today = datetime.now()
        pay_period_id = f"{today.year}-{today.month}-{1 if today.day <= 15 else 16}"
        
        # create or update the approval document for firestore
        approval_ref = db.collection('payroll_approvals').document(f"{location}_{pay_period_id}")
        approval_ref.set({
            'location': location,
            'pay_period_id': pay_period_id,
            'approved_at': firestore.SERVER_TIMESTAMP,
            'status': 'approved'
        })

        print(f"recorded payroll approved for {location} in pay period {pay_period_id}")
    except Exception as e:
        print(f"Error recording payroll approval for {location}: {e}")
        return {"status": "error", "message": str(e)}

def check_all_locations_approved():
    """
    Checks the 'payroll_approvals' collection in Firestore to see if all
    locations have submitted their approval for the current pay period.
    
    Returns:
        True if all locations are approved, False otherwise.
    """
    # Placeholder for logic to:
    # 1. Get the list of all locations from the `locations` variable.
    # 2. Determine the current pay period ID.
    # 3. Query Firestore to see how many approval documents exist for this pay period.
    # 4. Compare the count with the total number of locations.
    # approved_count = db.collection('payroll_approvals').where('pay_period_id', '==', current_pay_period_id).get()
    # return len(approved_count) == len(locations)
    try:
        today = datetime.now().date()
        pay_period_id = f"{today.year}-{today.month}-{1 if today.day <= 15 else 16}"


        approvals_ref = (
            db.collection('payroll_approvals') 
                .where('pay_period_id', '==', pay_period_id)    .stream()
        )

        approved_locations = {doc.to_dict().get('location') for doc in approvals_ref if doc.exists}
        
        all_approved = set(locations).issubset(approved_locations)
        
        print(f"Approved locations for {pay_period_id}: {approved_locations}")
        print(f"All locations approve? {all_approved}")
        
        return all_approved
    except Exception as e:
        print(f"Error checking approvals: {e}")
        return False
        
        

def send_final_approval_email():
    """
    Sends a final confirmation email to all admins, stating that payroll
    for all locations has been verified. This email contains all the
    individual location CSVs as attachments.
    """
    print("All locations approved. Sending final payroll summary email.")
    
    # 1. Get admin emails.
    admin_emails = get_admin_emails()
    if not admin_emails:
        print("No admin emails found. Cannot send final approval email")
        return
    
    # 2. Create the email message.
    msg = MIMEMultipart()
    msg['Subject'] = "Final Payroll Verification: All Locations Approved"
    body = "Payroll from all locations has been verified for the current pay period. Please find the summary CSVs attached."
    msg.attach(MIMEText(body, 'plain'))
    body = """
    Hello Admin Team,

    All locations have successfully approved their payroll for the current pay period. 
    Attached are the individual CSV summaries for each location.

    Regards,
    Payroll Automation System
    """
    msg.attach(MIMEText(body, "plain"))

    # 3. Fetch and attach the CSV data for each location.
    for location in locations:
        try:
            csv_data, _, _ = generate_payroll_data_for_location(location)
            if not csv_data or len(csv_data) <= 1:
                print(f"No data for {location}; skipping attachment.")
                continue

            filename = f"{location}_payroll_{datetime.now().strftime('%Y-%m-%d')}.csv"
            buffer = io.StringIO()
            writer = csv.writer(buffer)
            writer.writerows(csv_data)

            part = MIMEBase("application", "octet-stream")
            part.set_payload(buffer.getvalue().encode("utf-8"))
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={filename}")
            msg.attach(part)
        except Exception as e:
            print(f"Error generating CSV for {location}: {e}")


    #     # Logic to attach each CSV file to the email.
    
    # 4. Send the final consolidated email.
    # with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=ssl.create_default_context()) as server:
    #     server.login(SENDER_EMAIL, SENDER_PASSWORD)
    #     server.sendmail(SENDER_EMAIL, admin_emails, msg.as_string())
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        print("Final approval email sent successfully.")
    except Exception as e:
        print(f"Failed to send final approval email: {e}")
    
    print("Final approval email sent successfully.")

# --- Flask Route Integration ---
# In your app.py, you would add a route like this:
#
# from payroll_validation import handle_payroll_approval
#
# @app.route('/payroll/approve/<location>', methods=['POST'])
# def approve_payroll(location):
#     # Add authentication/authorization here to ensure only a Senior PM can trigger this.
#     # For example, check the user's role and their assigned location from the request's auth token.
#     # ...
#
#     result = handle_payroll_approval(location)
#     if result['status'] == 'success':
#         return jsonify(result), 200
#     else:
#         return jsonify(result), 500

def list_payroll_approvals():
    """
    Lists all locations that have submitted payroll approvals for the current pay period.
    Useful for admin monitoring or dashboard purposes.
    """
    try:
        today = datetime.now()
        pay_period_id = f"{today.year}-{today.month}-{1 if today.day <= 15 else 16}"
        docs = db.collection('payroll_approvals') \
                 .where('pay_period_id', '==', pay_period_id) \
                 .stream()
        return {doc.id: doc.to_dict() for doc in docs}
    except Exception as e:
        print(f"Error fetching approvals: {e}")
        return {}

def list_payroll_approvals():
    """
    Lists all locations that have submitted payroll approvals for the current pay period.
    Useful for admin monitoring or dashboard purposes.
    """
    try:
        today = datetime.now()
        pay_period_id = f"{today.year}-{today.month}-{1 if today.day <= 15 else 16}"
        docs = db.collection('payroll_approvals') \
                 .where('pay_period_id', '==', pay_period_id) \
                 .stream()
        return {doc.id: doc.to_dict() for doc in docs}
    except Exception as e:
        print(f"Error fetching approvals: {e}")
        return {}
