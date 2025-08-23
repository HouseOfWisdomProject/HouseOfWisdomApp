import React, { useState } from 'react';
import { FaHome, FaCalendarAlt, FaEllipsisH, FaUsers } from 'react-icons/fa';
import Calendar from '../components/Calendar';

const StaffDashboard = () => {
  const [activeTab, setActiveTab] = useState('Dashboard');

  const renderContent = () => {
    switch (activeTab) {
      case 'Dashboard':
        return (
          <div style={styles.dashboardContent}>
            <div style={styles.headerRow}>
                <h2 style={styles.shiftHeader}>My Tutor Dashboard</h2>
                <img src="/HOW-Logo.png" alt="HOW Logo" style={styles.logo} />
            </div>

            <div style={styles.quickAccessRow}>
              <div style={styles.hoursContainer}>
                <h3>Hours Worked This Week</h3>
                <div style={styles.grayBox}>--:--</div>
              </div>

              <div style={styles.quickAccessContainer}>
                <h3>Quick Access</h3>
                <div style={styles.quickAccessGrid}>
                  <button style={styles.quickButton}>+ Create New Report</button>
                  <button style={styles.quickButton}>Student Reports</button>
                  <button style={styles.quickButton}>Google Meets</button>
                  <button style={styles.quickButton}>Email</button>
                </div>
              </div>
            </div>

            <div>
              <h3>Weekly Schedule</h3>
              <div style={styles.grayBox}>Calendar for the week...</div>
            </div>
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

  return (
    <div style={styles.container}>
      <div style={styles.sidebar}>
        <div style={styles.profileSection}>
          <div style={styles.profilePic}></div>
          <div>
            <h4>Jane Doe</h4>
            <button style={styles.viewProfile}>View Profile</button>
          </div>
        </div>
        <div style={styles.navButtons}>
          {['Dashboard', 'Calendar', 'Shift Coverage', 'Onboarding'].map((item) => (
            <div
              key={item}
              style={{
                ...styles.navButton,
                ...(activeTab === item ? styles.activeNavButton : {})
              }}
              onClick={() => setActiveTab(item)}
            >
              <span style={styles.icon}>{
                item === 'Dashboard' ? <FaHome /> :
                item === 'Calendar' ? <FaCalendarAlt /> :
                item === 'Shift Coverage' ? <FaEllipsisH /> :
                <FaUsers />
              }</span>
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
    minHeight: '100vh',
    fontFamily: 'sans-serif',
    flexWrap: 'wrap',
  },
  headerRow: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    flexWrap: 'wrap',
    gap: '10px',
  },
  shiftHeader: {
    margin: 0,
    marginTop: '50px',
    fontSize: 'clamp(18px, 2vw, 28px)',
  },
  logo: {
    width: '100px',
    height: 'auto',
    maxWidth: '100%',
  },
  sidebar: {
    width: '250px',
    backgroundColor: '#ffefd5',
    padding: '20px',
    display: 'flex',
    flexDirection: 'column',
    gap: '20px',
    flexShrink: 0,
  },
  profileSection: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    flexWrap: 'wrap',
  },
  profilePic: {
    width: '50px',
    height: '50px',
    borderRadius: '50%',
    backgroundColor: '#ccc',
  },
  viewProfile: {
    backgroundColor: '#000',
    color: '#fff',
    border: 'none',
    padding: '5px 10px',
    fontSize: '12px',
    cursor: 'pointer',
  },
  navButtons: {
    display: 'flex',
    flexDirection: 'column',
    gap: '10px',
  },
  navButton: {
    backgroundColor: '#fff',
    color: '#333',
    padding: '10px',
    cursor: 'pointer',
    borderRadius: '5px',
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    flexWrap: 'wrap',
  },
  activeNavButton: {
    backgroundColor: '#fff',
    borderLeft: '6px solid #f97316',
    marginLeft: '-6px',
  },
  icon: {
    fontSize: '16px',
  },
  content: {
    flexGrow: 1,
    backgroundColor: '#fff',
    padding: '30px',
    minWidth: 0,
    overflowX: 'hidden',
  },
  dashboardContent: {
    display: 'flex',
    flexDirection: 'column',
    gap: '30px',
  },
  buttonRow: {
    display: 'flex',
    gap: '10px',
    flexWrap: 'wrap',
  },
  punchButton: {
    padding: '15px 30px',
    backgroundColor: '#f97316',
    fontSize: '16px',
    border: 'none',
    color: '#fff',
    borderRadius: '5px',
    cursor: 'pointer',
    marginTop: '-25px',
  },
  quickAccessRow: {
    display: 'flex',
    gap: '40px',
    flexWrap: 'wrap',
  },
  hoursContainer: {
    flex: 1,
    minWidth: '250px',
  },
  quickAccessContainer: {
    flex: 2,
    minWidth: '250px',
  },
  grayBox: {
    backgroundColor: '#eee',
    height: '100px',
    borderRadius: '10px',
    padding: '20px',
    marginTop: '10px',
    overflowX: 'auto',
  },
  quickAccessGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '10px',
    marginTop: '10px',
  },
  quickButton: {
    padding: '20px',
    backgroundColor: '#f97316',
    color: '#fff',
    fontSize: '15px',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
  },
};


export default StaffDashboard;