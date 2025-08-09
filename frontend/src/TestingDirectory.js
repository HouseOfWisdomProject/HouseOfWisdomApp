import React from 'react';

const TestingDirectory = () => {
  const handleTestClick = () => {
    console.log("Test button clicked!");
    alert("Test button clicked!");
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.heading}>Welcome to the House of Wisdom App Testing Directory</h1>
      <p style={styles.paragraph}>
        This page is designed to help with what page you want to test out!
      </p>
      <ul style={styles.list}>
        <li><code>/login</code> — Login Selection Page</li>
        <li><code>/login/student</code> — Student Login Page</li>
        <li><code>/login/staff</code> — Staff Login Page</li>
        <li><code>/tutordashboard</code> — Tutor Dashboard</li>
        <li><code>/admindashboard</code> — Admin Dashboard</li>
        <li><code>/seniordashboard</code> — Senior Project Manager Dashboard</li>
        <li><code>/juniordashboard</code> — Junior Project Manager Dashboard</li>
      </ul>
    </div>
  );
};

const styles = {
  container: {
    maxWidth: '600px',
    margin: '40px auto',
    padding: '20px',
    fontFamily: 'Arial, sans-serif',
    border: '1px solid #ccc',
    borderRadius: '10px',
    backgroundColor: '#fafafa',
    textAlign: 'center',
  },
  heading: {
    color: '#333',
  },
  paragraph: {
    fontSize: '16px',
    color: '#555',
  },
  list: {
    textAlign: 'left',
    margin: '20px 0',
    paddingLeft: '20px',
    color: '#444',
  },
};

export default TestingDirectory;