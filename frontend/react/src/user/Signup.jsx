import React, { useState } from 'react';
import Emergency from '../images/EmergencyRed.png';
import NineOneOne from '../images/119Orange.png';
import Extinguisher from '../images/extinguisher.png';
import Header from '../components/Header';

const Signup = () => {
    const [formData, setFormData] = useState({
        userId: '',
        password: '',
        confirmPassword: '',
        email: '',
        verificationCode: ''
    });

    const handleInputChange = (field, value) => {
        setFormData(prev => ({
            ...prev,
            [field]: value
        }));
    };

    // 엔터키 핸들러
    const handleKeyDown = (e, nextTabIndex) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            if (nextTabIndex) {
                const nextElement = document.querySelector(`[tabindex="${nextTabIndex}"]`);
                if (nextElement) {
                    nextElement.focus();
                }
            } else {
                // 마지막 입력칸에서는 회원가입 실행
                handleSignup();
            }
        }
    };

    const handleSignup = () => {
        console.log('회원가입 실행', formData);
        // 회원가입 로직
    };

    return (
        <>
            <Header />
            <div style={{
                width: "100%",
                minHeight: "calc(100vh - 45px)",
                background: "linear-gradient(to bottom, #fefaedff, #fff4dfff)",
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                position: "relative",
                padding: "20px 0"
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

                {/* 회원가입 전체 박스 */}
                <div style={{
                    width: "400px",
                    background: "#FFE4B5",
                    border: "2px solid #FF6B35",
                    borderRadius: "20px",
                    padding: "30px",
                    textAlign: "center",
                    boxShadow: "0 4px 8px rgba(0,0,0,0.1)",
                    overflowY: "auto"
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

                    {/* 회원가입 전체 박스 */}
                    <div style={{
                        width: "330px",
                        background: "white",
                        borderRadius: "20px",
                        padding: "20px",
                        textAlign: "center",
                        boxShadow: "0 4px 8px rgba(0,0,0,0.1)",
                    }}>
                        {/* Sign up 텍스트 */}
                        <h2 style={{
                            color: "#FF6B35",
                            fontSize: "22px",
                            fontWeight: "600",
                            marginBottom: "15px",
                            fontFamily: "Montserrat, sans-serif"
                        }}>Sign up</h2>

                        {/* 입력 필드들 */}
                        <div style={{ marginBottom: "12px", textAlign: "left" }}>
                            <label style={{
                                display: "block",
                                marginBottom: "5px",
                                fontSize: "13px",
                                fontWeight: "500"
                            }}>아이디 <span style={{ color: "red" }}>*</span></label>
                            <input
                                type="text"
                                value={formData.userId}
                                onChange={(e) => handleInputChange('userId', e.target.value)}
                                onKeyDown={(e) => handleKeyDown(e, "2")}
                                tabIndex="1"
                                style={{
                                    width: "100%",
                                    padding: "12px",
                                    border: "2px solid #ddd",
                                    borderRadius: "8px",
                                    fontSize: "14px",
                                    boxSizing: "border-box"
                                }}
                                placeholder="영문, 숫자 포함 8~12자"
                            />
                            <button style={{
                                width: "100%",
                                padding: "8px",
                                background: "#FF8C42",
                                color: "white",
                                border: "none",
                                borderRadius: "6px",
                                fontSize: "14px",
                                fontWeight: "500",
                                cursor: "pointer",
                                marginTop: "8px"
                            }}>중복체크</button>
                        </div>

                        <div style={{ marginBottom: "12px", textAlign: "left" }}>
                            <label style={{
                                display: "block",
                                marginBottom: "5px",
                                fontSize: "13px",
                                fontWeight: "500"
                            }}>비밀번호 <span style={{ color: "red" }}>*</span></label>
                            <input
                                type="password"
                                value={formData.password}
                                onChange={(e) => handleInputChange('password', e.target.value)}
                                onKeyDown={(e) => handleKeyDown(e, "3")}
                                tabIndex="2"
                                style={{
                                    width: "100%",
                                    padding: "12px",
                                    border: "2px solid #ddd",
                                    borderRadius: "8px",
                                    fontSize: "14px",
                                    boxSizing: "border-box"
                                }}
                                placeholder="영문, 숫자, 특수문자 포함 8~16자"
                            />
                        </div>

                        <div style={{ marginBottom: "12px", textAlign: "left" }}>
                            <label style={{
                                display: "block",
                                marginBottom: "5px",
                                fontSize: "13px",
                                fontWeight: "500"
                            }}>비밀번호 확인 <span style={{ color: "red" }}>*</span></label>
                            <input
                                type="password"
                                value={formData.confirmPassword}
                                onChange={(e) => handleInputChange('confirmPassword', e.target.value)}
                                onKeyDown={(e) => handleKeyDown(e, "4")}
                                tabIndex="3"
                                style={{
                                    width: "100%",
                                    padding: "12px",
                                    border: "2px solid #ddd",
                                    borderRadius: "8px",
                                    fontSize: "14px",
                                    boxSizing: "border-box"
                                }}
                                placeholder="비밀번호를 다시 입력하세요"
                            />
                        </div>

                        <div style={{ marginBottom: "15px", textAlign: "left" }}>
                            <label style={{
                                display: "block",
                                marginBottom: "5px",
                                fontSize: "13px",
                                fontWeight: "500"
                            }}>이메일 <span style={{ color: "red" }}>*</span></label>
                            <input
                                type="email"
                                value={formData.email}
                                onChange={(e) => handleInputChange('email', e.target.value)}
                                onKeyDown={(e) => handleKeyDown(e, "5")}
                                tabIndex="4"
                                style={{
                                    width: "100%",
                                    padding: "12px",
                                    border: "2px solid #ddd",
                                    borderRadius: "8px",
                                    fontSize: "14px",
                                    boxSizing: "border-box"
                                }}
                                placeholder="이메일을 입력하세요"
                            />
                            <button style={{
                                width: "100%",
                                padding: "8px",
                                background: "#FF8C42",
                                color: "white",
                                border: "none",
                                borderRadius: "6px",
                                fontSize: "14px",
                                fontWeight: "500",
                                cursor: "pointer",
                                marginTop: "8px"
                            }}>이메일 확인</button>
                        </div>

                        <div style={{ marginBottom: "10px", textAlign: "left" }}>
                            <label style={{
                                display: "flex",
                                justifyContent: "space-between",
                                alignItems: "center",
                                marginBottom: "5px",
                                fontSize: "13px",
                                fontWeight: "500"
                            }}>
                                <span>인증번호 입력 <span style={{ color: "red" }}>*</span></span>
                                <span style={{ color: "#FF6B35", fontSize: "12px" }}>02:15</span>
                            </label>
                            <input
                                type="text"
                                value={formData.verificationCode}
                                onChange={(e) => handleInputChange('verificationCode', e.target.value)}
                                onKeyDown={(e) => handleKeyDown(e, null)} // 마지막 입력칸
                                tabIndex="5"
                                style={{
                                    width: "100%",
                                    padding: "12px",
                                    border: "2px solid #ddd",
                                    borderRadius: "8px",
                                    fontSize: "14px",
                                    boxSizing: "border-box"
                                }}
                                placeholder="인증번호를 입력하세요"
                            />
                            <button style={{
                                width: "100%",
                                padding: "8px",
                                background: "#FF8C42",
                                color: "white",
                                border: "none",
                                borderRadius: "8px",
                                fontSize: "14px",
                                fontWeight: "500",
                                cursor: "pointer",
                                marginTop: "8px"
                            }}>인증번호 확인</button>
                        </div>

                        {/* 회원가입 버튼 */}
                        <button
                            onClick={handleSignup}
                            style={{
                                width: "100%",
                                padding: "8px",
                                background: "#D52222",
                                color: "white",
                                border: "none",
                                borderRadius: "8px",
                                fontSize: "14px",
                                fontWeight: "500",
                                cursor: "pointer",
                                marginTop: "5px",
                                marginBottom: "5px"
                            }}
                        >회원가입</button>
                    </div>
                </div>
            </div>
        </>
    );
};

export default Signup;