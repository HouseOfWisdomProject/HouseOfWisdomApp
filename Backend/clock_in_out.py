#get_staff_by_location(location): This function will query the Firestore database to get a 
#list of all users associated with a specific location. It will return a list of staff members, 
#including students, tutors, and project managers. Admins will be included in the lists for all locations.


#clock_in(user_id, location): This function will be called when a staff member clocks in. It will record 
#the current timestamp and log the event in a new Firestore collection, for example, clock_events.


#clock_out(user_id, location): This function will be called when a staff member clocks out. It will
#update the corresponding clock-in entry with the clock-out time and calculate the total duration 
#of the shift.

#get_location_roster(location): This function will fetch the list of staff members for a given location
#to be displayed on the Junior PM's device.