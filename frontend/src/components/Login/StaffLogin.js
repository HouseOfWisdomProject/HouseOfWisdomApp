import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const StaffLogin = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = async () => {
    setError(''); // reset error

    try {
      // Step 1: Login
      const loginRes = await fetch("/login/staff", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      let loginData;
      try {
        loginData = await loginRes.json();
      } catch (jsonErr) {
        console.error('Failed to parse login response as JSON', jsonErr);
        setError('Server returned invalid response');
        return;
      }

      if (!loginRes.ok) {
        console.error('Login failed:', loginData);
        setError(loginData.error || 'Login failed');
        return;
      }

      localStorage.setItem('idToken', loginData.idToken);
      localStorage.setItem('uid', loginData.uid);

      // Step 2: Fetch profile
      const profileRes = await fetch(`/user_profile/${loginData.uid}`);
      let profileData;
      try {
        profileData = await profileRes.json();
      } catch (jsonErr) {
        console.error('Failed to parse profile response as JSON', jsonErr);
        setError('Server returned invalid profile response');
        return;
      }

      if (!profileRes.ok) {
        console.error('Failed to fetch profile:', profileData);
        setError(profileData.error || 'Failed to fetch profile');
        return;
      }

      // Step 3: Redirect based on role
      const role = profileData.role;
      console.log('User role:', role);

      switch(role) {
        case 'admin':
          navigate('/admindashboard');
          break;
        case 'seniorProjectManager':
          navigate('/seniordashboard');
          break;
        case 'juniorProjectManager':
          navigate('/juniordashboard');
          break;
        case 'tutor':
          navigate('/tutordashboard');
          break;
        case 'student':
          navigate('/studentdashboard');
          break;
        default:
          console.warn('Unknown role, redirecting to default dashboard');
          navigate('/dashboard');
          break;
      }

    } catch (err) {
      console.error('Unexpected error during login:', err);
      setError('An unexpected error occurred');
    }
  };

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
          placeholder="Email"
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

        <button onClick={handleLogin} style={styles.button}>
          Login
        </button>

        {error && <p style={{ color: 'red' }}>{error}</p>}

        <a href="#" style={styles.link}>
          Forgot password?
        </a>
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
    position: 'relative',
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
    fontFamily: 'Arial, sans-serif',
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

export default StaffLogin;