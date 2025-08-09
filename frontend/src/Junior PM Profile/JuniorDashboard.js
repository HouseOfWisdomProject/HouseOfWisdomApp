import React, { useState, useRef, useEffect } from 'react';
import { FaHome, FaCalendarAlt, FaEllipsisH, FaUsers, FaClock, FaUserGraduate, FaPersonBooth, FaUser } from 'react-icons/fa';
import Calendar from '../components/Calendar';
import StudentAttendance from '../components/StudentAttendance';

{/*this is just test profiles to show Punch in/out system and the corresponding tutors*/}
const dummyStaff = [
  {
    id: 1,
    name: 'John Smith',
    position: 'Tutor',
    location: 'Edmonds Location',
    hours: '12:30',
    profilePic: '',
  },
  {
    id: 2,
    name: 'Mary Johnson',
    position: 'Staff',
    location: 'Lake City Location',
    hours: '08:15',
    profilePic: '',
  }
];

const JuniorPMDashboard = () => {
  const [activeTab, setActiveTab] = useState('Dashboard');
  const [selectedStaff, setSelectedStaff] = useState(null);
  const profileRef = useRef();

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (profileRef.current && !profileRef.current.contains(event.target)) {
        setSelectedStaff(null);
      }
    };
    if (selectedStaff) {
      document.addEventListener('mousedown', handleClickOutside);
    } else {
      document.removeEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [selectedStaff]);

  const renderContent = () => {
    switch (activeTab) {
      case 'Dashboard':
        return (
          <div style={styles.dashboardContent}>
            <div style={styles.headerRow}>
              <h2 style={styles.shiftHeader}>My Dashboard</h2>
              <img src="/HOW-Logo.png" alt="HOW Logo" style={styles.logo} />
            </div>

            <div style={styles.quickAccessRow}>
              <div style={styles.quickAccessContainer}>
                <h3>Quick Access</h3>
                <div style={styles.quickAccessGrid}>
                  <button style={styles.quickButton}>+ Create a HOW Account</button>
                  <button style={styles.quickButton}>Student Reports</button>
                  <button style={styles.quickButton}>Google Meets</button>
                  <button style={styles.quickButton}>Contact Information</button>
                </div>
              </div>
            </div>

            <div>
              <h3>Weekly Schedule</h3>
              <div style={styles.grayBox}>Calendar for the week...</div>
            </div>
          </div>
        );
      case 'Staff Clock In/Out':
        return (
          <div style={styles.dashboardContent}>
            <h3>Staff Clock In/Out</h3>
            <div style={styles.staffTable}>
              {dummyStaff.map(staff => (
                <div key={staff.id} style={styles.staffRow}>
                  <span style={styles.staffName} onClick={() => setSelectedStaff(staff)}>{staff.name}</span>
                  <div>
                    <button style={styles.punchButton}>Punch In</button>
                    <button style={styles.punchButton}>Punch Out</button>
                  </div>
                </div>
              ))}
            </div>
            {selectedStaff && (
              <div style={styles.profileModal} ref={profileRef}>
                <div style={styles.profileHeader}>Profile</div>
                <div style={styles.profileBody}>
                  <div style={styles.profilePic}></div>
                  <div>
                    <p><strong>Name:</strong> {selectedStaff.name}</p>
                    <p><strong>Position:</strong> {selectedStaff.position}</p>
                    <p><strong>Location:</strong> {selectedStaff.location}</p>
                    <p><strong>Hours this Week:</strong> {selectedStaff.hours}</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        );
      case 'Student Attendance':
        return (
          <div style={styles.dashboardContent}>
          <h3>Student Attendance</h3>
          <StudentAttendance />
        </div>
      );
      case 'Calendar':
        return (
          <div style={styles.dashboardContent}>
          <h3>Team Calendar</h3>
          <Calendar />
        </div>
      );
      case 'Shift Coverage':
      case 'Onboarding':
      default:
        return <div style={styles.dashboardContent}>Content for {activeTab}</div>;
    }
  };

  const navItems = ['Dashboard', 'Staff Clock In/Out', 'Student Attendance', 'Calendar', 'Onboarding', 'Shift Coverage'];

  return (
    <div style={styles.container}>
      <div style={styles.sidebar}>
        <div style={styles.profileSection}>
          <div style={styles.profilePic}></div>
          <div>
            <h4>Brian Doe</h4>
            <button style={styles.viewProfile}>View Profile</button>
          </div>
        </div>
        <div style={styles.navButtons}>
          {navItems.map((item) => (
            <div
              key={item}
              style={{
                ...styles.navButton,
                ...(activeTab === item ? styles.activeNavButton : {})
              }}
              onClick={() => {
                setActiveTab(item);
                setSelectedStaff(null);
              }}
            >
              <span style={styles.icon}>
                {item === 'Dashboard' ? <FaHome /> :
                  item === 'Calendar' ? <FaCalendarAlt /> :
                    item === 'Shift Coverage' ? <FaEllipsisH /> :
                      item === 'Onboarding' ? <FaUsers /> :
                        item == 'Student Attendance' ? <FaUser /> :
                        <FaClock />}
              </span>
              {item}
            </div>
          ))}
        </div>
      </div>
      <div style={styles.content}>{renderContent()}</div>
    </div>
  );
};

const styles = {
  container: {
    display: 'flex',
    height: '100vh',
    fontFamily: 'sans-serif'
  },
  headerRow: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  shiftHeader: {
    margin: 0,
    marginTop: '50px'
  },
  logo: {
    width: '100px',
    height: 'auto',
  },
  sidebar: {
    width: '250px',
    backgroundColor: '#ffefd5',
    padding: '20px',
    display: 'flex',
    flexDirection: 'column',
    gap: '20px'
  },
  profileSection: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px'
  },
  profilePic: {
    width: '50px',
    height: '50px',
    borderRadius: '50%',
    backgroundColor: '#ccc'
  },
  viewProfile: {
    backgroundColor: '#000',
    color: '#fff',
    border: 'none',
    padding: '5px 10px',
    fontSize: '12px',
    cursor: 'pointer',
    marginTop: '-8px'
  },
  navButtons: {
    display: 'flex',
    flexDirection: 'column',
    gap: '10px'
  },
  navButton: {
    backgroundColor: '#fff',
    color: '#333',
    padding: '10px',
    cursor: 'pointer',
    borderRadius: '5px',
    display: 'flex',
    alignItems: 'center',
    gap: '10px'
  },
  activeNavButton: {
    backgroundColor: '#fff',
    borderLeft: '6px solid #f97316',
    marginLeft: '-6px'
  },
  icon: {
    fontSize: '16px'
  },
  content: {
    flexGrow: 1,
    backgroundColor: '#fff',
    padding: '30px'
  },
  dashboardContent: {
    display: 'flex',
    flexDirection: 'column',
    gap: '30px'
  },
  quickAccessRow: {
    display: 'flex',
    gap: '40px'
  },
  hoursContainer: {
    flex: '1'
  },
  quickButton: {
    padding: '20px',
    backgroundColor: '#f97316',
    color: '#fff',
    fontSize: '15px',
    border: 'none',
    borderRadius: '8px',
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
  profileModal: {
    marginTop: '20px',
    padding: '20px',
    backgroundColor: '#ffefd5',
    borderRadius: '10px',
    width: '300px'
  },
  profileHeader: {
    fontWeight: 'bold',
    fontSize: '18px',
    marginBottom: '10px'
  },
  profileBody: {
    display: 'flex',
    gap: '15px',
    alignItems: 'flex-start'
  },
  quickAccessContainer: {
    flex: '2'
  },
  grayBox: {
    backgroundColor: '#eee',
    height: '100px',
    borderRadius: '10px',
    padding: '20px',
    marginTop: '10px',
  },
  quickAccessGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(2, 1fr)',
    gap: '10px',
    marginTop: '10px'
  }
};

export default JuniorPMDashboard;