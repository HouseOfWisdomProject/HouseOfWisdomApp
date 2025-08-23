import React, { useState, useEffect } from 'react';

const SeniorPayroll = () => {
  const [payrollData, setPayrollData] = useState([]);
  const [googleFormUrl, setGoogleFormUrl] = useState("");

  // Replace with actual auth info
  const userLocations = ["LocationA", "LocationB"];

  useEffect(() => {
    fetch("/payroll/approvals")
      .then(res => res.json())
      .then(data => {
        // Filter so Senior PM only sees their locations
        const filtered = Object.values(data).filter(loc => 
          userLocations.includes(loc.location)
        );
        setPayrollData(filtered);
      })
      .catch(() => setPayrollData([]));

    fetch("/config")
      .then(res => res.json())
      .then(cfg => setGoogleFormUrl(cfg.google_form_url))
      .catch(() => setGoogleFormUrl(""));
  }, []);

  const approveLocation = (location) => {
    fetch(`/payroll/approve/${location}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ role: "senior_pm" }),
    })
    .then(res => res.json())
    .then(msg => {
      alert(msg.message);
      if (msg.status === "success") {
        setPayrollData(data => 
          data.map(d => d.location === location ? { ...d, status: "approved" } : d)
        );
      }
    })
    .catch(() => alert("Failed to approve payroll."));
  };

  const notifyAdmin = () => {
    fetch("/payroll/notify-admin", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ role: "senior_pm" }),
    })
    .then(res => res.json())
    .then(msg => alert(msg.message))
    .catch(() => alert("Failed to notify admin."));
  };

  const allApproved = payrollData.length > 0 && payrollData.every(d => d.status === "approved");

  return (
    <div style={styles.container}>
      <h2>Payroll Validation (My Locations)</h2>

      {googleFormUrl && (
        <a href={googleFormUrl} target="_blank" rel="noopener noreferrer" style={styles.link}>
          Access Google Form Repository
        </a>
      )}

      <table style={styles.table}>
        <thead>
          <tr>
            <th style={styles.th}>Location</th>
            <th style={styles.th}>Status</th>
            <th style={styles.th}>Action</th>
          </tr>
        </thead>
        <tbody>
          {payrollData.length === 0 && (
            <tr>
              <td colSpan="3" style={{ textAlign: 'center', padding: '15px' }}>No payroll data available.</td>
            </tr>
          )}
          {payrollData.map(loc => (
            <tr key={loc.location}>
              <td style={styles.td}>{loc.location}</td>
              <td style={styles.td}>{loc.status || "pending"}</td>
              <td style={styles.td}>
                {loc.status !== "approved" && (
                  <button style={styles.button} onClick={() => approveLocation(loc.location)}>
                    Approve
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {allApproved && (
        <button style={{ ...styles.button, marginTop: "20px" }} onClick={notifyAdmin}>
          Notify Admin Payroll Ready
        </button>
      )}
    </div>
  );
};

const styles = {
  container: {
    padding: '20px',
    fontFamily: 'sans-serif',
  },
  link: {
    display: 'inline-block',
    marginBottom: '20px',
    color: '#e97634ff',
    fontWeight: 'bold',
    textDecoration: 'none',
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
  },
  th: {
    borderBottom: '2px solid #ccc',
    textAlign: 'left',
    padding: '10px',
  },
  td: {
    borderBottom: '1px solid #eee',
    padding: '10px',
  },
  button: {
    padding: '8px 15px',
    backgroundColor: '#e97634ff',
    color: '#fff',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
  },
};

export default SeniorPayroll;