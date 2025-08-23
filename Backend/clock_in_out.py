from datetime import datetime
from firebase_config import db  
from firebase_admin import firestore

TIMESTAMP_FILE = "sheet_timestamps.json"
DAYS_INTERVAL = 15
EMAIL_TO_SHARE = "howwa2020@gmail.com"

def get_current_timestamp(): 
    return datetime.pstnow().isoformat()

def log_to_firestore(event_type, user_id, timestamp, role, location):
    doc_ref = db.collection("shifts").document()
    doc_ref.set({
        "event": event_type,
        "user_id": user_id,
        "timestamp": timestamp,
        "location": location,
        "role": role
    })
#clock_in(user_id, location): This function will be called when a staff member clocks in. It will record 
#the current timestamp and log the event in a new Firestore collection, for example, clock_events.
def clock_in (user_id, location, role):
    timestamp = get_current_timestamp()
    log_to_firestore("clock-in", user_id, timestamp, role, location)
    #log to sheets here
    return {"status": "clocked in", "timestamp": timestamp}

#clock_out(user_id, location): This function will be called when a staff member clocks out. It will
#update the corresponding clock-in entry with the clock-out time and calculate the total duration 
#of the shift.
def clock_out (user_id, location, role):
    timestamp = get_current_timestamp()
    log_to_firestore("clock-out", user_id, timestamp, role, location)
    #log to sheets here
    return {"status": "clocked out", "timestamp": timestamp}

#get_location_roster(location): This function will fetch the list of staff members for a given location
#to be displayed on the Senior PM's device.
def get_location_roster(location):
    db = firestore.client()
    user_map = {}

    location_query = db.collection('users').where("tutoringLocation", "arrayContains", location)
    location_docs = location_query.queryStream()

    for doc in location_docs:
        user_map[doc.id] = doc.to_dict()    

    admin_query = db.collection('users').where("role", "==", "admin")
    admin_docs = admin_query.queryStream()
    
    for doc in admin_docs:
        if doc.id not in user_map:
            user_map[doc.id] = doc.to_dict()

    # Add uid to each dict for frontend
    roster_list = []
    for uid, info in user_map.items():
        info['uid'] = uid
        info['checkedIn'] = False
        roster_list.append(info)

    return roster_list


#15 Day Summary
