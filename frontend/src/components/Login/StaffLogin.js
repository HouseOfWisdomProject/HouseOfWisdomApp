import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const StaffLoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  return (
    <div style={styles.container}>
      <div style={styles.whitecard}>
        <div style={styles.backlinkcontainer}>
            <button onClick={() => navigate('/login')} style={styles.backLink}>
                ← Back
            </button>
        </div>
        <img src="/HOW-Logo.png" alt="HOW Logo" style={styles.logo} />
        <h2 style={styles.heading}>Staff Login Portal</h2>

        <input
          type="text"
          placeholder="Username or Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          style={styles.input}
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={styles.input}
        />

        <button style={styles.button}>Login</button>

        <a href="#" style={styles.link}>Forgot password?</a>
      </div>
    </div>
  );
};

const styles = {
container: {
    backgroundColor: '#fad7ad',
    height: '100vh',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
},
whitecard: {
    backgroundColor: 'white',
    padding: '70px 40px',
    borderRadius: '12px',
    boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
    textAlign: 'center',
    width: '90%',
    maxWidth: '400px',
},
backLink: {
    textDecoration: 'underline',
    color: '#333',
    fontSize: '14px',
    cursor: 'pointer',
    background: 'none',
    border: 'none',
    padding: 0,
    fontFamily: 'Arial, sans-serif',
},
backlinkcontainer: {
    position: 'absolute',
    padding: '10px 12px',  
    top: '16px',
    left: '20px',
    borderRadius: '7px',
    backgroundColor: 'white',
    zIndex: 10, 
},
logo: {
    width: '120px',
    marginBottom: '20px',
    marginTop: '-40px',
},
heading: {
    marginBottom: '30px',
    color: '#333',
    fontFamily: 'Arial',
},
input: {
    width: '100%',
    padding: '12px 16px',
    marginBottom: '20px',
    borderRadius: '6px',
    border: '1px solid #ccc',
    fontSize: '16px',
    boxSizing: 'border-box',    
    display: 'block',          
    fontFamily: 'Arial, sans-serif'
},
button: {
    backgroundColor: '#f97316',
    color: 'white',
    fontWeight: 'bold',
    padding: '13px 16px',
    borderRadius: '6px',
    border: 'none',
    fontSize: '18px',
    cursor: 'pointer',
    width: '100%',
    marginBottom: '16px',
    transition: 'background-color 0.3s ease',
},
link: {
    color: '#333',
    fontSize: '14px',
    textDecoration: 'underline',
    cursor: 'pointer',
},
};

export default StaffLoginPage;
