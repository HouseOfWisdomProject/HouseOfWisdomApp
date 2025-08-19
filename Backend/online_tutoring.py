# online_tutoring.py

"""
This file will contain the backend logic for creating, managing, and retrieving
information about online tutoring sessions. It will interface with the Firestore
database to store session details and tutor assignments.
"""

from firebase_config import db
from datetime import time
from firebase_admin import firestore
import re

# --- Firestore Data Model ---
#
# We'll use a collection called 'online_sessions' to store the tutoring sessions.
# Each document in this collection will represent a recurring weekly session.
#
# /online_sessions/{session_id}
#   - day_of_week: "Saturday" (e.g., "Monday", "Tuesday")
#   - start_time: "3:00 PM" (12-hour AM/PM format)
#   - end_time: "5:00 PM"
#   - tutors: [
#       {
#           "tutor_id": "uid_of_tutor_1",
#           "firstName": "John",
#           "lastName": "Doe",
#           "googleMeetsLink": "https://meet.google.com/xyz-abc-def"
#       },
#       {
#           "tutor_id": "uid_of_tutor_2",
#           "firstName": "Jane",
#           "lastName": "Smith",
#           "googleMeetsLink": "https://meet.google.com/ghi-jkl-mno"
#       }
#   ]
#

# --- Function Blueprints ---

valid_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Frinday", "Saterday", "Sunday"]

def create_online_session(day_of_week, start_time, end_time):
    """
    Creates a new recurring online tutoring session.

    Args:
        day_of_week (str): The day of the week for the session (e.g., "Saturday").
        start_time (str): The start time in "H:MM AM/PM" format (e.g., "3:00 PM").
        end_time (str): The end time in "H:MM AM/PM" format (e.g., "5:00 PM").

    Returns:
        dict: A confirmation message with the new session's ID.
    """
    # 1. Validate the input parameters.
    #    - Check if day_of_week is a valid day.
    #    - Check if start_time and end_time are valid time formats.
    #    - Ensure start_time is before end_time.
    # 2. Create a new document in the 'online_sessions' collection in Firestore.
    #    - The document data will include the day, start time, end time, and an empty 'tutors' array.
    # 3. Return the ID of the newly created session document.

    import re
    from datetime import datetime

    time_pattern = r"^(1[0-2]|0?[1-9]):[0-5][0-9] (AM|PM)$"

    # Validate day_of_week
    if day_of_week not in valid_days:
        return {"error": "Invalid day_of_week."}

    # Validate start_time and end_time
    if not re.match(time_pattern, start_time) or not re.match(time_pattern, end_time):
        return {"error": "Invalid time format. Use 'H:MM AM/PM'."}

    # Convert times to datetime objects for comparison
    fmt = "%I:%M %p"
    try:
        start_dt = datetime.strptime(start_time, fmt)
        end_dt = datetime.strptime(end_time, fmt)
    except ValueError:
        return {"error": "Invalid time format."}

    if start_dt >= end_dt:
        return {"error": "Start time must be before end time."}

    # Create the session document
    session_ref = db.collection("online_sessions").add({
        "day_of_week": day_of_week,
        "start_time": start_time,
        "end_time": end_time,
        "tutors": []
    })
    session_id = session_ref[1].id if isinstance(session_ref, tuple) else session_ref.id
    return {"message": "Session created successfully.", "session_id": session_id}

def delete_online_session(session_id):
    """
    Deletes an online tutoring session.

    Args:
        session_id (str): The unique ID of the session to delete.

    Returns:
        dict: A confirmation message.
    """
    # 1. Find the document in the 'online_sessions' collection with the given session_id.
    # 2. If the document exists, delete it.
    # 3. If not, return an error message.
    
    session_ref = db.collection("online_sessions").document(session_id)
    if session_ref.get().exists:
        session_ref.delete()
        return {"message": f"Session {session_id} deleted."}
    return {"error": "Session not found."}

def edit_online_session(session_id, new_day=None, new_start_time=None, new_end_time=None):
    """
    Edits the details of an existing online session.

    Args:
        session_id (str): The ID of the session to edit.
        new_day (str, optional): The new day of the week.
        new_start_time (str, optional): The new start time in "H:MM AM/PM" format.
        new_end_time (str, optional): The new end time in "H:MM AM/PM" format.

    Returns:
        dict: A confirmation message.
    """
    session_ref = db.collection("online_sessions").document(session_id)
    if not session_ref.get().exists:
        return {"error": "Session not found."}

    updates = {}

    if new_day:
        if new_day not in VALID_DAYS:
            return {"error": "Invalid day of week"}
        updates["day_of_week"] = new_day

    if new_start_time:
        if not validate_time_format(new_start_time):
            return {"error": "Invalid start time format"}
        updates["start_time"] = new_start_time

    if new_end_time:
        if not validate_time_format(new_end_time):
            return {"error": "Invalid end time format"}
        updates["end_time"] = new_end_time

    if not updates:
        return {"message": "No valid updates provided"}

    session_ref.update(updates)
    return {"message": "Session updated successfully"}
    
def validate_time_format(time_str):
    """Validates time in 'H:MM AM/PM' format."""
    return bool(re.match(r'^(1[0-2]|0?[1-9]):[0-5][0-9] (AM|PM)$', time_str))

def add_tutor_to_session(session_id, tutor_id):
    """
    Adds a tutor to a recurring online session.

    Args:
        session_id (str): The ID of the session.
        tutor_id (str): The UID of the tutor to add.

    Returns:
        dict: A confirmation message.
    """
    try:
        session_ref = db.collection('online_sessions').document(session_id)
        tutor_ref = db.collection('users').document(tutor_id)

        session_doc = session_ref.get()
        tutor_doc = tutor_ref.get()

        if not session_doc.exists:
            return {"error": "Session not found."}
        if not tutor_doc.exists:
            return {"error": "Tutor not found."}

        tutor_info = tutor_doc.to_dict()
        tutor_data = {
            "tutor_id": tutor_id,
            "firstName": tutor_info.get("firstName"),
            "lastName": tutor_info.get("lastName"),
            "googleMeetsLink": tutor_info.get("googleMeetsLink")
        }

        session_ref.update({"tutors": firestore.ArrayUnion([tutor_data])})
        return {"message": f"Tutor {tutor_id} added to session {session_id}."}
    except Exception as e:
        return {"error": f"An error occurred: {e}"}

def remove_tutor_from_session(session_id, tutor_id):
    """
    Removes a tutor from a recurring online session.

    Args:
        session_id (str): The ID of the session.
        tutor_id (str): The UID of the tutor to remove.

    Returns:
        dict: A confirmation message.
    """
    # 1. Fetch the session document from 'online_sessions'.
    # 2. Find the tutor object in the 'tutors' array that has the matching tutor_id.
    # 3. If found, remove that object from the array.
    #    - Use Firestore's arrayRemove for this operation.
    try:
        session_ref = db.collection("online_sessions").document(session_id)
        session_doc = session_ref.get()
        
        if not session_doc.exists:
            return {"error": "Session not found."}
        
        session_data = session_doc.to_dict()
        tutors = session_data.get("tutors", [])
        
        if tutor_to_remove = none
        for tutor in tutors: 
            if tutor.get("tutor_id") == tutor_id:
                tutor_to_remove = tutor
                break
    
        if tutor_to_remove:
            session_ref.update({
                "tutors": firestore.ArrayRemove([tutor_to_remove])
            })
            return {"message": f"Tutor {tutor_id} removed from session {session_id}."}
        else:
            return {"error": "Tutor not found in session."}
    except Exception as e:
        return {"error": str(e)}
            
            
            
def get_session_tutors(session_id):
    """
    Retrieves the details of all tutors in a specific session.

    Args:
        session_id (str): The ID of the session.

    Returns:
        list: A list of dictionaries, each containing a tutor's details.
    """
    # 1. Fetch the session document by its session_id.
    # 2. If the document exists, return the 'tutors' array.
    #    - The array will contain the firstName, lastName, and googleMeetsLink for each tutor.
    # 3. If the session is not found, return an empty list or an error.
    try:
        session_ref = db.collection("online_sessions").document(session_id)
        session_doc = session_ref.get()
        if session_doc.exists:
            return session_doc.to_dict().get("tutors", [])
        else:
            return {"error": "Session not found."}
    except Exception as e:
        return {"error": str(e)}

