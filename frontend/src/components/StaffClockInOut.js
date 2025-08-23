import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

const StaffClockInOut = () => {
  const [staffList, setStaffList] = useState([]);
  const [selectedStaff, setSelectedStaff] = useState(null);
  const [location] = useState('DefaultLocation'); // fixed location
  const [statusMessage, setStatusMessage] = useState('');
  const profileRef = useRef();

  useEffect(() => {
    fetchStaff();
  }, []);

  const fetchStaff = async () => {
    try {
      const response = await axios.get(`/roster/${location}`);
      const staffWithUid = response.data.map(staff => ({
        ...staff,
        checkedIn: false,
        uid: staff.uid,
      }));
      setStaffList(staffWithUid);
    } catch (err) {
      console.error('Error fetching roster:', err);
    }
  };

  const handleClockIn = async (uid) => {
    try {
      await axios.post('/clock_in', { user_id: uid, location, role: 'staff' });
      setStaffList(prev =>
        prev.map(s => (s.uid === uid ? { ...s, checkedIn: true } : s))
      );
      setStatusMessage('Clock-in successful!');
      setTimeout(() => setStatusMessage(''), 3000);
    } catch (err) {
      console.error('Failed to clock in:', err);
      setStatusMessage('Clock-in failed.');
      setTimeout(() => setStatusMessage(''), 3000);
    }
  };

  const handleClockOut = async (uid) => {
    try {
      await axios.post('/clock_out', { user_id: uid, location, role: 'staff' });
      setStaffList(prev =>
        prev.map(s => (s.uid === uid ? { ...s, checkedIn: false } : s))
      );
      setStatusMessage('Clock-out successful!');
      setTimeout(() => setStatusMessage(''), 3000);
    } catch (err) {
      console.error('Failed to clock out:', err);
      setStatusMessage('Clock-out failed.');
      setTimeout(() => setStatusMessage(''), 3000);
    }
  };

  return (
    <div style={styles.container}>
      {statusMessage && <p style={styles.message}>{statusMessage}</p>}

      <div style={styles.staffGrid}>
        {staffList.map((staff) => (
          <div key={staff.uid} style={styles.staffCard}>
            <p style={styles.name} onClick={() => setSelectedStaff(staff)}>
              {staff.firstName} {staff.lastName}
            </p>
            <p style={styles.status}>
              {staff.checkedIn ? '✅ Clocked In' : '❌ Not Clocked In'}
            </p>
            <div style={styles.buttonRow}>
              <button style={styles.clockInBtn} onClick={() => handleClockIn(staff.uid)}>
                Clock In
              </button>
              <button style={styles.clockOutBtn} onClick={() => handleClockOut(staff.uid)}>
                Clock Out
              </button>
            </div>
          </div>
        ))}
      </div>

      {selectedStaff && (
        <div style={styles.modalOverlay} onClick={() => setSelectedStaff(null)}>
          <div style={styles.profileModal} onClick={(e) => e.stopPropagation()}>
            <div style={styles.profileHeader}>Employee Profile</div>
            <div style={styles.profileBody}>
              <div style={styles.profilePic}></div>
              <div>
                <p>
                  <strong>Name:</strong> {selectedStaff.firstName} {selectedStaff.lastName}
                </p>
                <p>
                  <strong>Status:</strong> {selectedStaff.checkedIn ? '✅ Clocked In' : '❌ Not Clocked In'}
                </p>
                <p>
                  <strong>Location:</strong> {location}
                </p>
                <p>
                  <strong>Hours this Week:</strong> {selectedStaff.hours ?? 'N/A'}
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
    flexDirection: 'column',
    alignItems: 'center',
    padding: '10px',
    border: '1px solid #ccc',
    borderRadius: '5px',
    backgroundColor: '#fafafa'
  },
  name: { 
    fontSize: '16px', 
    cursor: 'pointer', 
    color: '#000', 
    fontWeight: 'bold',
    marginBottom: '5px'
  },
  status: {
    marginBottom: '10px',
    fontWeight: 'bold'
  },
  buttonRow: { 
    display: 'flex', 
    justifyContent: 'space-between', 
    gap: '10px' 
  },
  clockInBtn: {
    backgroundColor: '#1f9607',
    color: 'white',
    border: 'none',
    padding: '6px 10px',
    borderRadius: '5px',
    cursor: 'pointer'
  },
  clockOutBtn: {
    backgroundColor: '#c40d0d',
    color: 'white',
    border: 'none',
    padding: '6px 10px',
    borderRadius: '5px',
    cursor: 'pointer'
  },
  modalOverlay: {
    position: 'fixed',
    top: 0, left: 0,
    width: '100vw', height: '100vh',
    backgroundColor: 'rgba(0,0,0,0.5)',
    display: 'flex', justifyContent: 'center', alignItems: 'center',
    zIndex: 1000
  },
  profileModal: {
    backgroundColor: '#fff',
    borderRadius: '10px',
    border: '2px solid #707070',
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
  },
  profilePic: { 
    width: '60px', 
    height: '60px', 
    borderRadius: '50%', 
    backgroundColor: '#ccc' 
  }
};

export default StaffClockInOut;
