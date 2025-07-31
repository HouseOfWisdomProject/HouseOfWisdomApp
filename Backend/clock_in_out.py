from datetime import datetime
from app import db
from firebase_admin import firestore

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
    location_query = db.where("tutoringLocation", "arrayContains", location)
    admin_query = db.where("role", "==", "admin")

    location_docs = location_query.queryStream()
    admin_docs = admin_query.queryStream()

    user_map = {}
    for doc in location_docs:
        user_map[doc.id] = doc.to_dict()
    
    for doc in admin_docs:
        user_map[doc.id] = doc.to_dict()

    staff_list = list(user_map.values())
    return staff_list

