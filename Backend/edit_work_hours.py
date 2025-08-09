# edit_work_hours.py

"""
This file provides the backend functionality for Senior Project Managers to manage and
correct employee work hours. It allows for the editing, removal, and addition of shifts.

The functions are designed to be called from a user-friendly interface where the
Senior PM can select an employee from a list and a specific date. The system
then handles the necessary Firestore database operations based on the provided
information, without exposing technical details like Firebase UIDs to the end-user.
"""

# Import necessary tools for handling dates, connecting to the database, and Google Sheets
from datetime import datetime, timedelta
from firebase_config import db
from clock_in_out import get_location_roster
from logging_google_sheets import get_gspread_client
import gspread


def _regenerate_log_sheet(location):
    """
    (New Helper Function)
    Rewrites the entire log sheet for a given location for the current pay period.
    This function acts as the single source of truth for sheet updates, ensuring
    the sheet always matches the Firestore database.

    Args:
        location (str): The location for which to regenerate the sheet.
    """
    try:
        # Get the authorized connection to the Google Sheets API
        client = get_gspread_client()
        if not client:
            # If the connection fails, stop the function and report an error
            raise Exception("Failed to connect to Google Sheets.")

        # Open the specific Google Sheets workbook by its name
        workbook = client.open("House of Wisdom Log")

        # Get today's date to figure out the current pay period
        today = datetime.now().date()
        # Check if the day is after the 15th to determine the pay period
        if today.day > 15:
            # If it's after the 15th, the period is the 16th to the end of the month
            start_date = today.replace(day=16)
            end_date = (today.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        else:
            # Otherwise, the period is the 1st to the 15th
            start_date = today.replace(day=1)
            end_date = today.replace(day=15)
        
        # Create the exact name for the worksheet, e.g., "Everett - 2025-08-01 to 2025-08-15"
        sheet_name = f"{location} - {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"

        try:
            # Try to select the worksheet with that name
            worksheet = workbook.worksheet(sheet_name)
        except gspread.exceptions.WorksheetNotFound:
            # If the worksheet doesn't exist, create a new one
            worksheet = workbook.add_worksheet(title=sheet_name, rows="250", cols="10")

        # Delete all data currently in the sheet
        worksheet.clear()
        # Define the header columns in order
        header = ["Location", "Role", "First Name", "Last Name", "Timestamp", "Status"]
        # Add the header as the first row in the now-empty sheet
        worksheet.append_row(header, value_input_option='USER_ENTERED')

        # To work efficiently, first get all users at the location and store them in a map.
        # This avoids asking the database for a user's name every time we see their ID.
        users_ref = db.collection('users').where('tutoringLocation', 'array_contains', location).stream()
        users_map = {user.id: user.to_dict() for user in users_ref}
        
        # Define the exact start and end times for the database query
        start_datetime_iso = datetime.combine(start_date, datetime.min.time()).isoformat()
        end_datetime_iso = datetime.combine(end_date, datetime.max.time()).isoformat()

        # Ask Firestore for all shifts at this location within the pay period, sorted by time
        shifts_query = db.collection('shifts').where('location', '==', location).where('timestamp', '>=', start_datetime_iso).where('timestamp', '<=', end_datetime_iso).order_by('timestamp').stream()
        
        # Create an empty list to hold all the rows we're about to create
        rows_to_append = []
        # Loop through every single shift record that the database returned
        for shift in shifts_query:
            # Convert the Firestore document object into a more usable Python dictionary
            shift_data = shift.to_dict()
            # Get the user's unique ID from the shift record
            user_id = shift_data.get('user_id')
            # Look up that user's info (name, role) in the map we created earlier
            user_info = users_map.get(user_id)
            
            # Make sure we found the user's info before proceeding
            if user_info:
                # Assemble a list of values for the row in the correct order
                row = [
                    shift_data.get("location", ""),
                    user_info.get("role", ""),
                    user_info.get("firstName", ""),
                    user_info.get("lastName", ""),
                    shift_data.get("timestamp"),
                    shift_data.get("event")  # This will be 'clock-in' or 'clock-out'
                ]
                # Add the newly created row to our list of rows to append
                rows_to_append.append(row)
        
        # If the list of rows is not empty...
        if rows_to_append:
            # ...add all the rows to the Google Sheet in a single, efficient operation
            worksheet.append_rows(rows_to_append, value_input_option='USER_ENTERED')
        
        # Return a success message
        return {"message": f"Sheet for {location} regenerated successfully."}

    except Exception as e:
        # If any part of the 'try' block fails, this code runs
        print(f"Error regenerating sheet for {location}: {e}")
        return {"error": str(e)}


def find_user_by_name(location, first_name, last_name):
    """
    Helper function to find a user's ID and role by their name and location.
    """
    try:
        # Point to the 'users' collection in the database
        users_ref = db.collection('users')
        # Build a query to find a user where location, first name, and last name all match
        query = users_ref.where('tutoringLocation', 'array_contains', location).where('firstName', '==', first_name).where('lastName', '==', last_name)
        # Execute the query
        docs = query.stream()
        # Get the first result from the query, or None if no user was found
        user = next(docs, None)
        # If a user was found...
        if user:
            # ...return a dictionary with their unique ID and their role
            return {'id': user.id, 'role': user.to_dict().get('role')}
        # If no user was found, return None
        return None
    except Exception as e:
        print(f"Error finding user by name: {e}")
        return None


def find_shifts_for_user(user_id, date):
    """
    Helper function to retrieve all shifts for a specific user on a given date.
    Returns paired clock-in/out events.
    """
    try:
        # Get the exact start (midnight) and end (11:59:59 PM) of the given date
        start_dt = datetime.fromisoformat(f"{date}T00:00:00")
        end_dt = datetime.fromisoformat(f"{date}T23:59:59")
        
        # Ask the database for all shifts for this user on this day, sorted by time
        shifts_query = db.collection('shifts').where('user_id', '==', user_id).where('timestamp', '>=', start_dt.isoformat()).where('timestamp', '<=', end_dt.isoformat()).order_by('timestamp').stream()
        
        # Get all the found shifts into a list to easily work with them
        shifts = list(shifts_query)
        # Create an empty list to store the final, paired-up shifts
        paired_shifts = []
        
        # A counter to keep track of our position in the list of shifts
        i = 0
        # Loop through the list of shifts as long as our counter is valid
        while i < len(shifts):
            # Get the current shift document and its data
            shift_doc = shifts[i]
            shift_data = shift_doc.to_dict()
            # Check if the current shift is a 'clock-in'
            if shift_data.get('event') == 'clock-in':
                # If it is, this is the start of a potential pair
                clock_in_doc = shift_doc
                # Check if there is a next item in the list AND if that item is a 'clock-out'
                if i + 1 < len(shifts) and shifts[i+1].to_dict().get('event') == 'clock-out':
                    # If so, we have found a complete pair
                    clock_out_doc = shifts[i+1]
                    # Create a dictionary holding all the info for this single shift
                    paired_shifts.append({
                        'clock_in_id': clock_in_doc.id,
                        'clock_out_id': clock_out_doc.id,
                        'start_time': clock_in_doc.to_dict()['timestamp'],
                        'end_time': clock_out_doc.to_dict()['timestamp']
                    })
                    # We've processed two items (in and out), so jump ahead by 2
                    i += 2
                else:
                    # If we found a clock-in but no matching clock-out, it's an incomplete shift.
                    # Just move to the next item to keep searching.
                    i += 1
            else:
                # If the current item is not a 'clock-in', just move to the next one
                i += 1
        # Return the list of complete, paired shifts
        return paired_shifts
    except Exception as e:
        print(f"Error finding shifts for user: {e}")
        return []

def edit_work_hours(location, clock_in_id, clock_out_id, new_start_time, new_end_time):
    """
    Allows a Senior PM to edit the clock-in and clock-out times for a specific shift.
    """
    try:
        # Find the clock-in document by its ID and update its timestamp
        db.collection('shifts').document(clock_in_id).update({'timestamp': new_start_time})
        # Find the clock-out document by its ID and update its timestamp
        db.collection('shifts').document(clock_out_id).update({'timestamp': new_end_time})
        
        # Call our helper function to update the Google Sheet with the corrected data
        _regenerate_log_sheet(location)
        
        # Return a success message
        return {"message": "Shift updated successfully."}
    except Exception as e:
        print(f"Error editing work hours: {e}")
        return {"error": str(e)}

def remove_shift(location, clock_in_id, clock_out_id):
    """
    Removes a specific shift (both clock-in and clock-out records) for a user.
    """
    try:
        # Find the clock-in document by its ID and delete it
        db.collection('shifts').document(clock_in_id).delete()
        # Find the clock-out document by its ID and delete it
        db.collection('shifts').document(clock_out_id).delete()

        # Call our helper function to update the Google Sheet so the shift is removed
        _regenerate_log_sheet(location)
        
        # Return a success message
        return {"message": "Shift removed successfully."}
    except Exception as e:
        print(f"Error removing shift: {e}")
        return {"error": str(e)}


def add_shift(location, first_name, last_name, start_time, end_time):
    """
    Adds a new shift (clock-in and clock-out) for a user on a specified day.
    """
    try:
        # First, find the user's info using their name and location
        user_info = find_user_by_name(location, first_name, last_name)
        # If no user is found, stop and return an error
        if not user_info:
            return {"error": "User not found."}
        
        # Get the user's unique ID and role from the info we found
        user_id = user_info['id']
        role = user_info['role']
        
        # Create the 'clock-in' record in the database
        db.collection('shifts').add({
            'event': 'clock-in',
            'user_id': user_id,
            'timestamp': start_time,
            'location': location,
            'role': role
        })
        
        # Create the 'clock-out' record in the database
        db.collection('shifts').add({
            'event': 'clock-out',
            'user_id': user_id,
            'timestamp': end_time,
            'location': location,
            'role': role
        })

        # Call our helper function to update the Google Sheet with the new shift included
        _regenerate_log_sheet(location)
        
        # Return a success message
        return {"message": "Shift added successfully."}
    except Exception as e:
        print(f"Error adding shift: {e}")
        return {"error": str(e)}
