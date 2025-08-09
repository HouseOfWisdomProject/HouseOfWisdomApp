import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

// Test UI locally
const dummyStaffList = [
  { id: 1, firstName: 'Mary', lastName: 'Johnson', checkedIn: false },
  { id: 2, firstName: 'John', lastName: 'Smith', checkedIn: false },
  { id: 3, firstName: 'Barbara', lastName: 'Lee', checkedIn: false }
];

const StaffClockInOut = () => {
  const [staffList, setStaffList] = useState([]);
  const [selectedStaff, setSelectedStaff] = useState(null);
  const [location] = useState('DefaultLocation'); // fixed location
  const [statusMessage, setStatusMessage] = useState('');
  const profileRef = useRef();

  useEffect(() => {
    // Replace with API call when backend is ready
    setStaffList(dummyStaffList);
  }, []);

  const fetchStaff = async () => {
    try {
      const response = await axios.get(`/get_roster?location=${location}`);
      setStaffList(response.data);
    } catch (error) {
      console.error('Error fetching roster:', error);
    }
  };

  const handleClockIn = async (id) => {
    try {
      await axios.post(`/api/staff/${id}/clock-in`);
      setStaffList(prev =>
        prev.map(s => (s.id === id ? { ...s, checkedIn: true, hours: s.hours + 1 } : s))
      );
    } catch (err) {
      console.error('Failed to clock in:', err);
      // Dummy fallback
      setStaffList(prev =>
        prev.map(s => (s.id === id ? { ...s, checkedIn: true, hours: s.hours + 1 } : s))
      );
    }
  };

  const handleClockOut = async (id) => {
    try {
      await axios.post(`/api/staff/${id}/clock-out`);
      setStaffList(prev =>
        prev.map(s => (s.id === id ? { ...s, checkedIn: false } : s))
      );
    } catch (err) {
      console.error('Failed to clock out:', err);
      // Dummy fallback
      setStaffList(prev =>
        prev.map(s => (s.id === id ? { ...s, checkedIn: false } : s))
      );
    }
  };
  return (
    <div style={styles.container}>
      {statusMessage && <p style={styles.message}>{statusMessage}</p>}

      <div style={styles.staffGrid}>
        {staffList.map((staff) => (
          <div key={staff.id} style={styles.staffCard}>
            <p
              style={styles.name}
              onClick={() => setSelectedStaff(staff)}
            >
              {staff.firstName} {staff.lastName}
            </p>
            <p style={styles.status}>
              {staff.checkedIn ? '✅ Clocked In' : '❌ Not Clocked In'}
            </p>
            <div style={styles.buttonRow}>
              <button 
                style={styles.clockInBtn} 
                onClick={() => handleClockIn(staff.id)}>Clock In</button>
              <button 
                style={styles.clockOutBtn} 
                onClick={() => handleClockOut(staff.id)}>Clock Out</button>
            </div>
          </div>
        ))}
      </div>

      {selectedStaff && (
        <div 
          style={styles.modalOverlay} 
          onClick={() => setSelectedStaff(null)}
        >
          <div 
            style={styles.profileModal} 
            onClick={(e) => e.stopPropagation()} // prevents closing when clicking inside
          >
            <div style={styles.profileHeader}>Employee Profile</div>
            <div style={styles.profileBody}>
              <div style={styles.profilePic}></div>
              <div>
                <p>
                  <strong>Name:</strong> {selectedStaff.firstName} {selectedStaff.lastName}
                </p>
                <p>
                  <strong>Status:</strong>{' '}
                  {selectedStaff.checkedIn ? '✅ Clocked In' : '❌ Not Clocked In'}
                </p>
                <p>
                  <strong>Location:</strong> {location}
                </p>
                <p>
                  <strong>Hours this Week:</strong>{' '}
                  {selectedStaff.hours ?? 'N/A'}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const styles = {
  container: {
    padding: '20px',
    fontFamily: 'Arial, sans-serif',
    textAlign: 'center'
  },
  message: {
    color: 'green',
    fontWeight: 'bold'
  },
  staffGrid: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '10px'
  },
  staffCard: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '10px',
    border: '1px solid #ccc',
    borderRadius: '5px',
    backgroundColor: '#fafafa'
  },
  name: {
    fontSize: '16px',
    cursor: 'pointer',
    color: '#000000',
    fontWeight: 'bold'
  },
  role: {
    fontSize: '14px',
    color: '#666'
  },
  buttonRow: {
    marginTop: '10px',
    display: 'flex',
    justifyContent: 'space-around'
  },
  clockInBtn: {
    backgroundColor: '#1f9607ff',
    marginRight: '10px',
    marginBottom: '3px',
    color: 'white',
    border: 'none',
    padding: '6px 10px',
    borderRadius: '5px',
    cursor: 'pointer'
  },
  clockOutBtn: {
    backgroundColor: '#c40d0dff',
    marginRight: '10px',
    marginBottom: '3px',
    color: 'white',
    border: 'none',
    padding: '6px 10px',
    borderRadius: '5px',
    cursor: 'pointer'
  },
  staffTable: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '10px'
  },
  staffRow: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '10px',
    border: '1px solid #eee',
    borderRadius: '5px',
    backgroundColor: '#fafafa'
  },
  staffName: {
    cursor: 'pointer',
    color: '#000000'
  },
  punchButton: {
    padding: '8px 16px',
    backgroundColor: '#f97316',
    color: '#fff',
    border: 'none',
    borderRadius: '5px',
    marginLeft: '5px',
    cursor: 'pointer'
  },
  modalOverlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    width: '100vw',
    height: '100vh',
    backgroundColor: 'rgba(0,0,0,0.5)',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1000
  },
  profileModal: {
    backgroundColor: '#ffffff',
    borderRadius: '10px',
    border: '2px solid #707070ff',
    fontSize: '17px',
    width: '300px',
    padding: '30px 60px',
    boxShadow: '0 4px 8px rgba(0,0,0,0.2)'
  },
  profileHeader: {
    fontWeight: 'bold',
    fontSize: '21px',
    marginBottom: '10px'
  },
  profileBody: {
    display: 'flex',
    gap: '15px',
    alignItems: 'flex-start'
  }
};

export default StaffClockInOut;
