import React, { useState } from 'react';

const Header = () => {
    const [isLoggedIn, setIsLoggedIn] = useState(false); // 임시 상태

    // 페이지 이동 함수
    const navigateToLogin = () => {
        window.location.href = '/user/login';
    };

    const navigateToSignup = () => {
        window.location.href = '/user/signup';
    };

    return (
        <header
            style={{
                width: "100%",
                height: "45px",
                background: "#b52929ff",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                color: "white",
                padding: "0 10px"
            }}>
            <p style={{
                margin: 0,
                fontFamily: "'Playfair Display', serif", // 고급스러운 세리프
                fontSize: "20px",
                fontWeight: 800,
                letterSpacing: "1px"
            }}>Emergency 119</p>
            {isLoggedIn ? (
                <div>
                    <span>사용자님 환영합니다!</span>
                    <button onClick={() => setIsLoggedIn(false)}>로그아웃</button>
                </div>
            ) : (
                <div style={{ display: "flex", alignItems: "center" }}>
                    <button 
                        onClick={navigateToLogin}
                        style={{
                            background: "transparent",
                            border: "none",
                            color: "white",
                            marginRight: "20px",
                            fontSize: "14px",
                            fontWeight: "500",
                            cursor: "pointer",
                            textDecoration: "none"
                        }}
                    >
                        로그인
                    </button>
                    <button 
                        onClick={navigateToSignup}
                        style={{
                            background: "transparent",
                            border: "none",
                            color: "white",
                            fontSize: "14px",
                            fontWeight: "500",
                            cursor: "pointer",
                            textDecoration: "none"
                        }}
                    >
                        회원가입
                    </button>
                </div>
            )}
        </header>
    );
};

export default Header;