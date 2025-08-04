import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LoginSelection from './components/Login/LoginSelection';
import StudentLogin from './components/Login/StudentLogin';
import StaffLogin from './components/Login/StaffLogin';
import SignUp from './components/Login/SignUp';
import Dashboard from './Tutor & PM Dashboard/StaffDashboard';
import AdminDashboard from './SeniorPM & Admin Dashboard/AdminDashboard';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<LoginSelection />} />
        <Route path="/login/student" element={<StudentLogin />} />
        <Route path="/login/staff" element={<StaffLogin />} />
        <Route path="/login/signup" element={<SignUp />} />
        <Route path="/staffdashboard" element={<Dashboard />} />
        <Route path="/admindashboard" element={<AdminDashboard />} />
      </Routes>
    </Router>
  );
}

export default App;