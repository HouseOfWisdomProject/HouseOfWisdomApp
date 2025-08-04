import React from 'react';
import { useNavigate } from 'react-router-dom';

const LoginSelection = () => {
  const navigate = useNavigate();

  return (
    <div style={styles.pageBackground}>
      <div style={styles.whiteContainer}>
        <img src="/HOW-Logo.png" alt="HOW Logo" style={styles.logo} />
        <h1 style={styles.heading}>Welcome to the House of Wisdom!</h1>

        <div style={styles.buttonRow}>
          <button style={styles.button} onClick={() => navigate('/login/student')}>
            Student Login
          </button>
          <button style={styles.button} onClick={() => navigate('/login/staff')}>
            Staff Login
          </button>
        </div>
      </div>
    </div>
  );
};

const styles = {
  pageBackground: {
    backgroundColor: '#fad7ad',
    minHeight: '100vh',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
  },
  whiteContainer: {
    backgroundColor: 'white',
    borderRadius: '16px',
    padding: '50px 40px',
    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
    maxWidth: '420px',
    width: '90%',
    textAlign: 'center',
  },
  logo: {
    width: '120px',
    marginBottom: '10px',
    marginTop: '1px',
  },
  heading: {
    marginBottom: '30px',
    color: '#333',
    fontFamily: 'Arial',
    fontWeight: 'bold',
  },
  buttonRow: {
    display: 'flex',
    justifyContent: 'center',
    gap: '12px',
    flexWrap: 'wrap',
    marginBottom: '30px',
  },
  button: {
    backgroundColor: '#f97316',
    color: 'white',
    fontWeight: 'bold',
    padding: '13px 16px',
    borderRadius: '6px',
    border: 'none',
    fontSize: '18px',
    transition: 'background-color 0.3s ease',
    cursor: 'pointer',
    width: '200px',
  },
};

const styleSheet = document.createElement("style");
styleSheet.type = "text/css";
styleSheet.innerText = `
  button:hover {
    background-color: #ea580c !important;
  }

  body, html {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }
`;
document.head.appendChild(styleSheet);

export default LoginSelection;
