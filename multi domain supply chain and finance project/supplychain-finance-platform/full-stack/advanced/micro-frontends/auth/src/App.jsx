import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './components/Login';
import Register from './components/Register';
import './App.css';

const App = () => {
  const [user, setUser] = useState(null);

  return (
    <Router basename="/auth">
      <div className="auth-micro-frontend">
        <Routes>
          <Route path="/login" element={<Login setUser={setUser} />} />
          <Route path="/register" element={<Register />} />
          <Route path="*" element={<Login setUser={setUser} />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;