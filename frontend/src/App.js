import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import TestDirectory from './TestingDirectory';
import LoginSelection from './components/Login/LoginSelection';
import StudentLogin from './components/Login/StudentLogin';
import StaffLogin from './components/Login/StaffLogin';
import TutorDashboard from './Tutor Profile/TutorDashboard';
import AdminDashboard from './Admin Profile/AdminDashboard';
import SeniorPMDashboard from './Senior PM Profile/SeniorDashboard';
import JuniorPMDashboard from './Junior PM Profile/JuniorDashboard';
import StudentDashboard from './Student Profile/StudentDashboard';
import CreateProfile from './Admin Profile/CreateProfile';

function App() {
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetch("/api/test")
      .then((res) => res.json())
      .then((data) => setMessage(data.message))
      .catch((err) => console.error("Error fetching:", err));
  }, []);

  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<TestDirectory />} />
          <Route path="/login" element={<LoginSelection />} />
          <Route path="/login/student" element={<StudentLogin />} />
          <Route path="/login/staff" element={<StaffLogin />} />
          <Route path="/tutordashboard" element={<TutorDashboard />} />
          <Route path="/admindashboard" element={<AdminDashboard />} />
          <Route path="/seniordashboard" element={<SeniorPMDashboard />} />
          <Route path="/juniordashboard" element={<JuniorPMDashboard />} />
          <Route path="/studentdashboard" element={<StudentDashboard />} />
          <Route path="/admin/createprofile" element={<CreateProfile />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
