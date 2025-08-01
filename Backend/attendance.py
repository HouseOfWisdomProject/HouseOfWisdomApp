# attendance.py
from datetime import datetime
from firebase_config import db

def get_student_list(location):
    """
    Retrieves a list of all students registered at a specific tutoring location.
    This function will query the Firestore 'users' collection to find all documents
    where the 'role' is 'student' and the 'tutoringLocation' array contains
    the specified location.
    
    Args:
        location (str): The name of the tutoring location (e.g., 'Everett').

    Returns:
        list: A list of dictionaries, where each dictionary represents a student's profile.
              Returns an empty list if no students are found.
    """
    pass

def take_attendance(location, student_id, status):
    """
    Records a student's attendance for the current day at a specific location.
    This function will create or access a document in the 'attendance' collection
    for the current date and location. It will then log the student's status
    ('present' or 'absent') along with a timestamp.

    Args:
        location (str): The tutoring location where attendance is being taken.
        student_id (str): The unique ID (UID) of the student.
        status (str): The attendance status, should be either 'present' or 'absent'.

    Returns:
        dict: A confirmation message of the action.
    """
    pass

def edit_attendance(location, student_id, status):
    """
    Edits an existing attendance record for a student on the current day.
    This is useful if a student's status was marked incorrectly and needs to be
    changed from 'absent' to 'present' or vice-versa. It will update the
    existing record with the new status and an 'last_edited' timestamp.

    Args:
        location (str): The tutoring location.
        student_id (str): The unique ID (UID) of the student whose record needs editing.
        status (str): The new attendance status ('present' or 'absent').

    Returns:
        dict: A confirmation message of the update.
    """
    pass

def attendance_count(location):
    """
    Calculates and returns the total number of students marked as 'present'
    at a specific location for the current day. This function will query the
    'attendance' collection for the given location and date.

    Args:
        location (str): The tutoring location.

    Returns:
        dict: A dictionary containing the location, the count of present students,
              and the date of the count.
    """
    pass