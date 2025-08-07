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
            worksheet = create_new_sheet(workbook, sheet_name)
            
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


#Code that creates a new sheet every 15 days
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

