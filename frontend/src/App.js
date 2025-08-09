import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import TestDirectory from './TestingDirectory';
import LoginSelection from './components/Login/LoginSelection';
import StudentLogin from './components/Login/StudentLogin';
import StaffLogin from './components/Login/StaffLogin';
import TutorDashboard from './Tutor Profile/TutorDashboard';
import AdminDashboard from './Admin Profile/AdminDashboard';
import SeniorPMDashboard from './Senior PM Profile/SeniorDashboard';
import JuniorPMDashboard from './Junior PM Profile/JuniorDashboard';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<TestDirectory />} />
        <Route path="/login" element={<LoginSelection />} />
        <Route path="/login/student" element={<StudentLogin />} />
        <Route path="/login/staff" element={<StaffLogin />} />
        <Route path="/tutordashboard" element={<TutorDashboard />} />
        <Route path="/admindashboard" element={<AdminDashboard />} />
        <Route path="/seniordashboard" element={<SeniorPMDashboard />} />
        <Route path="/juniordashboard" element={<JuniorPMDashboard />} />
      </Routes>
    </Router>
  );
}

export default App;