import React, { useState } from 'react';
import Emergency from '../images/EmergencyRed.png';
import NineOneOne from '../images/119Orange.png';
import Extinguisher from '../images/extinguisher.png';
import Header from '../components/Header';

const Login = () => {
  const [userId, setUserId] = useState('');
  const [password, setPassword] = useState('');
  const navigateToFindid = () => {
    window.location.href = '/user/findid';
  };

  const navigateToResetpw = () => {
    window.location.href = '/user/resetpw';
  };
  const navigateToSignup = () => {
    window.location.href = '/user/signup';
  };

  return (
    <>
      <Header />
      <div style={{
        width: "100%",
        height: "calc(100vh - 45px)",
        background: "linear-gradient(to bottom, #fefaedff, #fff4dfff)",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        position: "relative"
      }}>

        {/* 소화기 이미지 - 오른쪽 하단 */}
        <img
          src={Extinguisher}
          alt="소화기"
          style={{
            cursor: "pointer",
            position: "absolute",
            bottom: "20px",
            right: "20px",
            width: "80px",
            height: "auto"
          }}
        />

        {/* 로그인 전체 박스 */}
        <div style={{
          width: "400px",
          background: "#FFE4B5",
          border: "2px solid #FF6B35",
          borderRadius: "20px",
          padding: "20px 30px",
          textAlign: "center",
          boxShadow: "0 4px 8px rgba(0,0,0,0.1)"
        }}>

          {/* 로고 부분 */}
          <div style={{
            borderRadius: "15px",
            padding: "10px"
          }}>
            <img
              src={Emergency}
              alt="Emergency"
              style={{
                width: "220px",
                height: "auto",
                marginBottom: "3px"
              }}
            />
            <img
              src={NineOneOne}
              alt="119"
              style={{
                width: "100px",
                height: "auto"
              }}
            />
          </div>

          {/* 로그인 내부 박스 */}
          <div style={{
            width: "330px",
            background: "white",
            borderRadius: "20px",
            padding: "20px",
            textAlign: "center",
            marginBottom: "10px",
            boxShadow: "0 4px 8px rgba(0,0,0,0.1)",
          }}>

            {/* Log in 텍스트 */}
            <h2 style={{
              color: "#FF6B35",
              fontSize: "24px",
              fontWeight: "600",
              marginBottom: "20px",
              fontFamily: "Montserrat, sans-serif"
            }}>Log in</h2>

            {/* 입력 필드들 */}
            <div style={{ marginBottom: "15px", textAlign: "left" }}>
              <label style={{
                display: "block",
                marginBottom: "5px",
                fontSize: "14px",
                fontWeight: "500"
              }}>아이디</label>
              <input
                type="text"
                value={userId}
                onChange={(e) => setUserId(e.target.value)}
                style={{
                  width: "100%",
                  padding: "12px",
                  border: "2px solid #ddd",
                  borderRadius: "8px",
                  fontSize: "14px",
                  boxSizing: "border-box"
                }}
                placeholder="아이디를 입력하세요"
              />
            </div>

            <div style={{ marginBottom: "25px", textAlign: "left" }}>
              <label style={{
                display: "block",
                marginBottom: "5px",
                fontSize: "14px",
                fontWeight: "500"
              }}>비밀번호</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                style={{
                  width: "100%",
                  padding: "12px",
                  border: "2px solid #ddd",
                  borderRadius: "8px",
                  fontSize: "14px",
                  boxSizing: "border-box"
                }}
                placeholder="비밀번호를 입력하세요"
              />
            </div>

            {/* 로그인 버튼 */}
            <button style={{
              width: "100%",
              padding: "8px",
              background: "#D52222",
              color: "white",
              border: "none",
              borderRadius: "8px",
              fontSize: "14px",
              fontWeight: "500",
              cursor: "pointer",
              marginBottom: "5px"
            }}>로그인</button>
          </div>
          {/* 하단 링크들 */}
          <div style={{
            fontSize: "14px",
            color: "#FF6B35",
            marginTop: "20px"
          }}>
            <span onClick={navigateToSignup} style={{ cursor: "pointer", marginRight: "10px" }}>회원가입</span>
            <span>|</span>
            <span onClick={navigateToFindid} style={{ cursor: "pointer", margin: "0 10px" }}>아이디 찾기</span>
            <span>|</span>
            <span onClick={navigateToResetpw} style={{ cursor: "pointer", marginLeft: "10px" }}>비밀번호 재설정</span>
          </div>
        </div>
      </div>
    </>
  );
};

export default Login;