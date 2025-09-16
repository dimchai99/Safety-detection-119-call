# 안전감지 자동화 119 호출 서비스 — 기술 설계 문서

작성일: 2025-09-16 (KST)
작성자: 3조

---

## 1. 목표와 범위

- **목표**: 센서/모바일 이벤트로 위험을 조기에 감지하고, 사용자 확인을 거쳐 보호자·경비실·119 연결을 **신속/신뢰성 있게** 지원하는 서비스.
- **핵심 요구**
    - 실시간 이벤트 수집(≤ 1–3s), 인시던트 생성, 다단계 알림/에스컬레이션
    - 휴먼‑인‑더‑루프(확인/취소), 오탐 피드백, 감사로그
    - 운영 신뢰성(재시도/아이템포턴시, 모니터링, 백업/DR)
- **비범위(초기)**
    - 119 기관과의 직접 API 연동(공식 표준 부재) → **원클릭 발신 유도** 또는 보안실/지자체 연계로 대체

---

## 2. 전체 아키텍처 (하이레벨)

[Edge/Apps] ──HTTPS/MQTT/WebSocket──> [API Gateway + FastAPI Ingress]

                                                                                                  │

                                                                                                 ▼

                                                                       [Message Broker (Redis Streams)]

                                                                                                  │

                                                                           [Worker: Rules + ML Scoring]

                                                                                                  │

                                                           ┌──────────────┴──────────────┐

                                                          ▼                                                                           ▼

                                              [Supabase/Postgres]                                     [Notifier (SMS/Push/Call)]

                                               events/incidents/...                                           (Webhook/DLR 수신)

                                                          │                                                                             │

                                                          └──────────────────────► [Admin/User Portal]

### 구성요소

- **Ingress API(FastAPI)**: 인증/HMAC 검증, 아이템포턴시 키 생성, 브로커로 게시
- **브로커(Redis Streams/Kafka)**: 비동기 분리, 재시도/소비율 확장
- **워커**: 규칙엔진 + ML 스코어링 → 위험등급 결정, 인시던트/알림 생성
- **DB(Supabase/Postgres)**: 데이터/권한/RLS, 감사로그, 룰 정의
- **알림 엔진**: Push/SMS/카카오/음성발신(IVR/TTS) 전송 및 DLR 수집
- **포털(Flask/FastAPI + FE)**: 실시간 대시보드, 규칙 관리, 타임라인

---

## 3. 핵심 데이터 모델 (DDL 초안)

- 사용자/권한
- 장치/프로필
- 원시 이벤트(고빈도)
- 인시던트(사건 단위)
- 알림 전송 및 결과
- 에스컬레이션 단계
- 휴먼 컨펌(앱/웹에서 “신고/취소”)
- 감사 로그
- 룰/정책(UI로 수정 가능)

---

## 4. API 설계 (요점)

- `POST /ingest` (장치/앱 이벤트 수집; HMAC 또는 JWT 검증, **idempotency-key** 헤더 지원)
- `POST /incident/{id}/ack` (앱에서 “위험 확인/취소”)
- `POST /webhook/delivery-report` (SMS/카카오/콜 벤더 DLR 수신)
- `GET /incidents?status=open` (대시보드)
- `POST /rules` / `PUT /rules/{id}` (관리자만)

---

## 5. 메시지 처리 파이프라인

- 규칙 우선 차단/즉시 알림: “연기 센서 연속 10초 이상 HIGH”
- ML 스코어 보정: “가스 센서 + 온도 + 모션”의 다변량 이상치 스코어
- **최종 리스크 = max(규칙등급, ML등급)** 혹은 가중 결합
- 결과를 `events.risk_score, risk_level` 로 기록 → incident 판단.

---

## 6. 알림/에스컬레이션 정책 (초안)

- **1단계(0s)**: 앱 푸시 + 카카오 알림톡/SMS (링크로 ‘신고/해제’ 버튼 제공)
- **2단계(10s 타임아웃)**: 미응답 → 보호자/경비실 음성발신(IVR/TTS)
- **3단계(30s 타임아웃)**: 여전히 미응답 → **앱에서 119 원클릭 발신 안내**(법·운영 리스크 고려)
    - 실제 자동 통화 연결은 법·오탐 리스크가 커서, **사용자 확인 기반 연결**을 권장
- 각 채널의 **전송/수신/실패**는 `alerts` 와 `escalations` 테이블로 추적, 재시도/백오프

---

## 7. 보안/컴플라이언스

- **SLO**: 인지-to-알림 < 3초(로컬/브로커), E2E < 10초(모바일 푸시 포함)
- **DR/재시도**: 알림 채널 별 3-5회 지수 백오프, DLQ 격리
- **Idempotency**: 장치 타임스탬프 기준 키로 중복 삽입 방지
- **서명/HMAC** + 장치 발급 키, 서버측 **JWT(+Supabase RLS)**
- **PII 최소화**: 위치/전화번호는 별도 암호화 저장 또는 접근제어

---

## 8. 관측성/운영

- **실시간 인시던트 보드**: 상태 필터(open/ack/escalated/resolved), 지도 표시
- **타임라인**: 이벤트 → 알림 → 컨펌/에스컬 로그를 시간순으로
- **규칙 관리**: 임계치/지속시간/조합 조건 UI
- **오탐 피드백**: false positive 라벨 누적 → 모델/룰 자동 보정
- **감사로그**: 누가 언제 무엇을 바꿨는지

---

## 9. 배포/인프라

- **Docker**: FastAPI API, Worker, Frontend, Nginx(리버스 프록시)
- **옵션**: Kubernetes(수평 확장), HorizontalPodAutoscaler(ingest/worker)
- **관측성**:
    - Logs: JSON 구조화 + ELK/Opensearch
    - Metrics: Prometheus + Grafana 대시보드(알림 전송 실패율, E2E 지연, incident 폭주 감지)
    - Errors: Sentry

---

## 10. 개발 순서 / 스프린트 체크리스트

### 전체 전략

- **백엔드 골격 먼저 구축 → 룰 기반 MVP → 데이터 라벨 수집 → 모델 프로토타입 → 온라인 서빙**
- 이유: 서비스 신뢰성과 실제 데이터 확보가 우선, 모델은 후속으로 자연스럽게 붙일 수 있음.

- [ ]  `ingest` 라우트 + HMAC 서명
- [ ]  Redis Streams(또는 단순 Celery/RQ) 워커 1개
- [ ]  규칙 2~3개 하드코딩(연기/가스/낙상) + 리스크 맵핑
- [ ]  HIGH 이상 시 **Incident 생성 + Push/SMS 전송**
- [ ]  푸시/문자 링크로 **Confirm/Cancel API** 연결 → 에스컬 단계 구동
- [ ]  어드민 페이지(incidents, alerts, escalations 조회)
- [ ]  Supabase 테이블 및 RLS(사용자 자신의 장치/인시던트만 읽기)

---

## 11. 향후 과제

(동일, 생략 — v0.1 참고)