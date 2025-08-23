import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const CreateProfile = () => {
    const navigate = useNavigate();

    const [formData, setFormData] = useState({
        firstName: '',
        lastName: '',
        email: '',
        password: '',
        role: 'Student', // set default 
        gradeLevel: '',  //student
        parentContact: '', // student
    });

    const [message, setMessage] = useState('');
    const [error, setError] = useState('');

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');
    setError('');

    const roleMap = {
        'Student': 'student',
        'Tutor': 'tutor',
        'Junior PM': 'juniorProjectManager',
        'Senior PM': 'seniorProjectManager'
    };

    try {
        const response = await axios.post('/register', {
        ...formData,
        role: roleMap[formData.role]
        });

        // ← Place it here
        if (response.status === 201) {
        setMessage(`User ${formData.role} created successfully!`);
        setFormData({
            firstName: '',
            lastName: '',
            email: '',
            password: '',
            role: 'Student',
            gradeLevel: '',
            parentContact: '',
        });
        }

    } catch (err) {
        console.error(err);
        setError(err.response?.data?.error || 'An error occurred while creating the user.');
    }
};

  return (
    <div style={styles.container}>
      <div style={styles.whitecard}>
        <div style={styles.backlinkcontainer}>
          <button onClick={() => navigate('/admindashboard')} style={styles.backLink}>
            ← Back
          </button>
        </div>

        <img src="/HOW-Logo.png" alt="HOW Logo" style={styles.logo} />

        <h2 style={styles.heading}>Create a HOW Account</h2>

        {message && <p style={styles.success}>{message}</p>}
        {error && <p style={styles.error}>{error}</p>}

        <form onSubmit={handleSubmit} style={styles.form}>
          <input
            type="text"
            name="firstName"
            placeholder="First Name"
            value={formData.firstName}
            onChange={handleChange}
            required
            style={styles.input}
          />
          <input
            type="text"
            name="lastName"
            placeholder="Last Name"
            value={formData.lastName}
            onChange={handleChange}
            required
            style={styles.input}
          />
          <input
            type="email"
            name="email"
            placeholder="Email"
            value={formData.email}
            onChange={handleChange}
            required
            style={styles.input}
          />
          <input
            type="password"
            name="password"
            placeholder="Password"
            value={formData.password}
            onChange={handleChange}
            required
            style={styles.input}
          />

          <select
            name="role"
            value={formData.role}
            onChange={handleChange}
            style={styles.input}
          >
            <option>Student</option>
            <option>Tutor</option>
            <option>Junior PM</option>
            <option>Senior PM</option>
          </select>

          {formData.role === 'Student' && (
            <>
              <input
                type="text"
                name="gradeLevel"
                placeholder="Grade Level"
                value={formData.gradeLevel}
                onChange={handleChange}
                style={styles.input}
              />
              <input
                type="text"
                name="parentContact"
                placeholder="Parent Contact Info"
                value={formData.parentContact}
                onChange={handleChange}
                style={styles.input}
              />
            </>
          )}

          <button type="submit" style={styles.button}>Create Account</button>
        </form>
      </div>
    </div>
  );
};

const styles = {
  container: {
    backgroundColor: '#fad7ad',
    height: '125vh',
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
    marginTop: '-20px',
    maxWidth: '400px',
    position: 'relative',
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
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '15px',
  },
  input: {
    width: '100%',
    padding: '12px 16px',
    borderRadius: '6px',
    border: '1px solid #ccc',
    fontSize: '16px',
    boxSizing: 'border-box',
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
    marginTop: '10px',
    transition: 'background-color 0.3s ease',
  },
  success: {
    color: 'green',
    fontWeight: 'bold',
    marginBottom: '10px',
  },
  error: {
    color: 'red',
    fontWeight: 'bold',
    marginBottom: '10px',
  },
};

export default CreateProfile;