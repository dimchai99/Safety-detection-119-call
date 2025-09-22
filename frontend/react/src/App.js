import React from 'react';
import './App.css';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Home from './components/Homepage';
import HeroSection from './user/HeroSection';
import Login from './user/Login';
import Signup from './user/Signup';
import Findid from './user/Findid';
import Resetpw from './user/Resetpw';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>

          
          {/* /homepage 경로에서 Home 컴포넌트 표시 */}
          <Route path="/" element={<HeroSection />} />
          <Route path="/user/login" element={<Login />} />
          <Route path="/user/signup" element={<Signup />} />
          <Route path="/user/findid" element={<Findid />} />
          <Route path="/user/resetpw" element={<Resetpw />} />
          

          
          {/* 404 페이지 */}
          <Route path="*" element={<div>페이지를 찾을 수 없습니다.</div>} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;