# attendance_google_sheet.py
from logging_google_sheets import get_gspread_client
from datetime import datetime, timedelta
from calendar import monthrange
import gspread
from firebase_config import db
from attendance import get_student_list
from locations import locations

def micro_attendance(google_sheet_name, location):
    """
    Creates a daily attendance report for a specific location in a dedicated Google Sheet.

    Args:
        google_sheet_name (str): The name of the Google Sheet to write the report to.
        location (str): The specific location to generate the report for.
    """
    try:
        # Authenticate with Google Sheets and get the client.
        client = get_gspread_client()
        if not client:
            print("Failed to get Google Sheets client.")
            return

        # Open the specified Google Sheet by its name.
        try:
            workbook = client.open(google_sheet_name)
        except gspread.exceptions.SpreadsheetNotFound:
            print(f"Spreadsheet '{google_sheet_name}' not found. Please create it first.")
            return

        # Create a name for the new worksheet/tab based on the current date.
        date_str = datetime.now().strftime('%Y-%m-%d')
        
        # Check if a worksheet with today's date already exists.
        try:
            worksheet = workbook.worksheet(date_str)
            worksheet.clear() # Clear existing data to overwrite with fresh data.
        except gspread.exceptions.WorksheetNotFound:
            # If not, create a new one.
            worksheet = workbook.add_worksheet(title=date_str, rows="100", cols="10")
        
        # Define and add the header row.
        header = ["First Name", "Last Name", "Status"]
        worksheet.append_row(header, value_input_option='USER_ENTERED')

        # Fetch the list of all students for the given location.
        student_list = get_student_list(location)
        if 'error' in student_list:
            print(f"Error fetching student list: {student_list['error']}")
            return

        # Fetch today's attendance data from Firestore.
        attendance_ref = db.collection('attendance').document(f"{location}_{date_str}")
        attendance_doc = attendance_ref.get()
        attendance_data = attendance_doc.to_dict().get('student', {}) if attendance_doc.exists else {}

        # Prepare rows for batch update.
        rows_to_append = []
        for student in student_list:
            student_id = student.get('id')
            first_name = student.get('firstName', '')
            last_name = student.get('lastName', '')
            
            # Determine student's attendance status.
            status = attendance_data.get(student_id, {}).get('status', 'Unmarked')
            
            rows_to_append.append([first_name, last_name, status])

        # Append all student attendance data to the worksheet.
        if rows_to_append:
            worksheet.append_rows(rows_to_append, value_input_option='USER_ENTERED')
        
        print(f"Successfully updated attendance for {location} in '{google_sheet_name}' for {date_str}.")

    except Exception as e:
        print(f"An error occurred in micro_attendance: {e}")

def macro_attendance():
    """
    Calculates and records the monthly average attendance for all locations.
    This function is intended to be run on the first day of a new month.
    It creates a new worksheet for each year.
    """
    # This function should run only on the first day of the month.
    if datetime.now().day != 1:
        print("Macro attendance report is only generated on the first day of the month.")
        return

    try:
        # Authenticate with Google Sheets.
        client = get_gspread_client()
        if not client:
            print("Failed to get Google Sheets client.")
            return

        # Open the summary workbook.
        workbook = client.open("HOW-Monthly-Attendance-Summary")

        # Determine the date range and year for the *previous* month.
        today = datetime.now()
        last_month_end = today.replace(day=1) - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)
        report_year_str = str(last_month_start.year)
        _, num_days_in_month = monthrange(last_month_start.year, last_month_start.month)
        
        # Check if worksheet for the report's year exists, if not, create it.
        try:
            worksheet = workbook.worksheet(report_year_str)
        except gspread.exceptions.WorksheetNotFound:
            worksheet = workbook.add_worksheet(title=report_year_str, rows="100", cols="20")
            # Create and append the header row for the new yearly sheet.
            header = ["Month/Year"] + locations + ["Total Average"]
            worksheet.append_row(header, value_input_option='USER_ENTERED')
            print(f"Created new worksheet for the year {report_year_str}.")

        # Prepare the row with the month and year as the first column.
        month_year_str = last_month_start.strftime("%-m/%y")
        new_row = [month_year_str]
        grand_total_present = 0

        # Loop through each location to calculate its average attendance.
        for location in locations: # Using the list from locations.py
            # Query Firestore for all attendance docs for the location in the last month.
            query = db.collection('attendance').where('location', '==', location).where('date', '>=', last_month_start.strftime('%Y-%m-%d')).where('date', '<=', last_month_end.strftime('%Y-%m-%d'))
            docs = query.stream()

            location_total_present = 0
            for doc in docs:
                data = doc.to_dict().get('student', {})
                present_count = sum(1 for s in data.values() if s.get('status') == 'present')
                location_total_present += present_count
            
            # Calculate average and add to the row.
            avg_attendance = round(location_total_present / num_days_in_month, 2) if num_days_in_month > 0 else 0
            new_row.append(avg_attendance)
            grand_total_present += location_total_present

        # Calculate the overall average across all locations.
        total_avg = round(grand_total_present / num_days_in_month, 2) if num_days_in_month > 0 else 0
        new_row.append(total_avg)

        # Append the summary row to the correct yearly Google Sheet.
        worksheet.append_row(new_row, value_input_option='USER_ENTERED')

        print(f"Successfully generated macro attendance summary for {month_year_str} in sheet '{report_year_str}'.")

    except Exception as e:
        print(f"An error occurred in macro_attendance: {e}")