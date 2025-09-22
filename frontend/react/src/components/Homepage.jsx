import React, { useState, useEffect } from 'react';
import './Home.css';

const Home = () => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(30);
  const [activeNav, setActiveNav] = useState(0);
  const [currentTime, setCurrentTime] = useState('11:30');
  const [stats, setStats] = useState({
    fire: 100,
    smoke: 52.7,
    hazard: 45.2
  });

  // 시간 업데이트
  useEffect(() => {
    const timeInterval = setInterval(() => {
      const now = new Date();
      const timeStr = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;
      setCurrentTime(timeStr);
    }, 30000);

    return () => clearInterval(timeInterval);
  }, []);

  // 진행바 업데이트
  useEffect(() => {
    const progressInterval = setInterval(() => {
      if (isPlaying) {
        setProgress(prev => prev >= 100 ? 0 : prev + 1);
      }
    }, 500);

    return () => clearInterval(progressInterval);
  }, [isPlaying]);

  // 스탯 업데이트
  useEffect(() => {
    const statsInterval = setInterval(() => {
      setStats({
        fire: Math.floor(Math.random() * 100),
        smoke: Math.floor(Math.random() * 100),
        hazard: Math.floor(Math.random() * 100)
      });
    }, 5000);

    return () => clearInterval(statsInterval);
  }, []);

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const handleNavClick = (index) => {
    setActiveNav(index);
  };

  const navItems = [
    '실시간 모니터링',
    '이벤트 로그/타임라인',
    '상세 현황',
    '지도 기반 뷰'
  ];

  const alerts = [
    { time: currentTime, message: '화재 센즈 감지 !', type: 'fire' },
    { time: currentTime, message: '화재 발생🔥', type: 'normal' },
    { time: currentTime, message: '119 호출 가능🚨', type: 'emergency' }
  ];

  return (
    <div className="home-container">
      <div className="header">
        <h1>Emergency 119</h1>
        <div className="header-right">firedragon002님 안녕하세요! 로그아웃</div>
      </div>
      
      <div className="nav-bar">
        {navItems.map((item, index) => (
          <div
            key={index}
            className={`nav-item ${activeNav === index ? 'active' : ''}`}
            onClick={() => handleNavClick(index)}
          >
            {item}
          </div>
        ))}
      </div>
      
      <div className="main-container">
        <div className="left-panel">
          <div className="video-container">
            <div className="panel-header">
              실시간 모니터링
              <button className="search-btn">검색</button>
            </div>
            <div className="video-display">
              <div className="building building1"></div>
              <div className="building building2"></div>
              <div className="building building3"></div>
              <div className="fire-incident fire1">FIRE</div>
              <div className="fire-incident fire2">FIRE</div>
            </div>
            <div className="video-controls">
              <button className="play-btn" onClick={handlePlayPause}>
                {isPlaying ? '⏸' : '▶'}
              </button>
              <span>1:18 / 1:40</span>
              <div className="progress-bar">
                <div className="progress" style={{ width: `${progress}%` }}></div>
              </div>
              <span>설정</span>
            </div>
          </div>
        </div>
        
        <div className="right-panel">
          <div className="greeting-card">
            <div className="mascot">🤠</div>
            <div className="greeting-text">안전해요 😊</div>
          </div>
          
          <div className="stats-container">
            <div className="stats-grid">
              <div className="stat-item fire-stat">
                <div className="stat-label">Fire</div>
                <div className="stat-value">Max : {stats.fire}%</div>
              </div>
              <div className="stat-item smoke-stat">
                <div className="stat-label">Smoke</div>
                <div className="stat-value">Max : {stats.smoke}%</div>
              </div>
              <div className="stat-item hazard-stat">
                <div className="stat-label">Hazard</div>
                <div className="stat-value">Max : {stats.hazard}%</div>
              </div>
            </div>
          </div>
          
          <div className="alerts-section">
            <div className="alerts-header">실시간 알림 🔔</div>
            {alerts.map((alert, index) => (
              <div key={index} className="alert-item">
                <div className="alert-time">{alert.time}</div>
                <div className={`alert-${alert.type}`}>{alert.message}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;