#This file will handle all interactions with the Google Sheets API. It will be responsible for
#updating the location-specific spreadsheets with real-time data from the clock-in/out system.

#update_spreadsheet(location, data): This function will take the location and the clock-in/out
#data as input and update the corresponding Google Sheet. It will be responsible for authenticating
#with the Google Sheets API, selecting the correct sheet, and appending the new data.
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv  # Import dotenv
from datetime import datetime, timedelta
from locations import locations
import json

# Load environment variables from .env file
load_dotenv()

#Function to authenticate with Google Sheets API
def get_gspread_client():
    """Authenticates with Google and returns a gspread client."""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    #Get the credetnials path from the environment variable
    creds_path = os.getenv("GOOGLE_CREDENTIALS_PATH")
    if not creds_path:
        print("Google credentials path not set. Please set the GOOGLE_CREDENTIALS_PATH environment variable.")
        return None

    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        print(f"Authentication failed: {e}")
        return None

def update_spreadsheet(location, data):
    """Upadtes the Google Sheet for the specified location with the provided data.
    
    Args:
        Location (str): the name of the location sheet to update.
        data (list): a list containing the clock-in/out data to append.
    """
    client = get_gspread_client()

    try:
        workbook = client.open("House of Wisdom Log")
        #Today's date
        today = datetime.now().date() 
        start_date = today - timedelta(days = today.day % 15)
        end_date = start_date + timedelta(days = 14)
        sheet_name = f"{location} - {start_date.strftime('%Y-%m-%d')} to {end_date.strfttime('%Y-%m-%d')}"
        
        try:
            worksheet = workbook.worksheet(sheet_name)
        
        except gspread.exceptions.WorksheetNotFound():
            worksheet = workbook.add_worksheet(title = sheet_name, rows = "250", cols = "10")
            header = ["Location", "Role", "First Name", "Last Name", "Timestamp", "Status"]
            worksheet.append_row(header, value_input_option='USER ENTERED')
            
        row = [
            location,
            data.get("role", ""),
            data.get("firstName", ""),
            data.get("lastName", ""),
            data.get("timestamp"),
            data.get("status")
        ]

        worksheet.append_row(row)
        print(f"Appended row to {sheet_name}: {row}")
    
    except Exception as e:
        print(f"Error updating spreadsheet for location '{location}': {e}")

def create_new_sheet(workbook, sheet_name):
    """
    Creates a new worksheet within the given workbook, adds a header, and returns it.
    
    Args:
        workbook (gspread.Spreadsheet): The spreadsheet to add the worksheet to.
        sheet_name (str): The name for the new worksheet.
    
    Returns:
        gspread.Worksheet: The newly created worksheet object, or None if creation fails.
    """
    try:
        print(f"Worksheet '{sheet_name}' not found. Creating it now...")
        # Add a new worksheet with the specified title.
        worksheet = workbook.add_worksheet(title=sheet_name, rows="250", cols="10")
        
        # Define and add the header row.
        header = ["Location", "Role", "First Name", "Last Name", "Timestamp", "Status"]
        worksheet.append_row(header, value_input_option='USER_ENTERED')
        
        print(f"Successfully created worksheet '{sheet_name}' and added header.")
        return worksheet
    except Exception as e:
        print(f"Failed to create new worksheet '{sheet_name}': {e}")
        return None

# In google_sheets.py
def generate_15_day_location_summary(location):
    """
    Calculates total work hours for each user at a specific location over the
    last 15 days and writes a summary report to a new Google Sheet.
    """
    print(f"Generating 15-day summary report for {location}...")
    
    # 1. Define the 15-day date range (MODIFIED LOGIC)
    # This logic now matches the update_spreadsheet function.
    today = datetime.now().date()
    start_date = today - timedelta(days = (today.day - 1) % 15)
    end_date = start_date + timedelta(days=14)
    
    try:
        from firebase_config import db 

        # ... (The rest of the function remains the same) ...
        users_query = db.collection('users').where('tutoringLocation', 'array-contains', location).stream()
        location_users = {user.id: user.to_dict() for user in users_query}
        report_data = []

        for user_id, user_data in location_users.items():
            total_duration = timedelta()
            shifts_ref = db.collection('shifts').where('user_id', '==', user_id).where('location', '==', location).order_by('timestamp').stream()
            
            clock_in_time = None
            for shift in shifts_ref:
                shift_data = shift.to_dict()
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

        if not report_data:
            print(f"No work hour data found for {location} in the period starting {start_date}.")
            return {"message": f"No work hour data found for {location} in the period."}

        # This part correctly creates a sheet name based on the date bucket.
        client = get_gspread_client()
        if not client:
            raise Exception("Could not connect to Google Sheets.")
            
        workbook = client.open("HOW-15-Day-Summary")
        sheet_name = f"{location} Summary - {start_date.strftime('%Y-%m-%d')}"
        
        try:
            worksheet = workbook.worksheet(sheet_name)
            worksheet.clear() 
        except gspread.exceptions.WorksheetNotFound:
            worksheet = workbook.add_worksheet(title=sheet_name, rows="100", cols="10")
        
        header = ["First Name", "Last Name", "Role", "Total Hours (15-day Period)"]
        worksheet.append_row(header)
        worksheet.append_rows(report_data)

        print(f"Successfully generated summary for {location} in sheet: {sheet_name}")
        return {"message": f"Report successfully generated for {location}."}

    except Exception as e:
        print(f"An error occurred during report generation for {location}: {e}")
        raise
