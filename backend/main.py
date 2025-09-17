# main.py
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

# 초기화 모듈 임포트 (엔진/세션 준비)
from app.core.config import PORT
from app.core import db as _  # noqa: F401  (엔진 초기화용 임포트)

# 라우터 등록
from app.routers.health import router as health_router
from app.routers.ingest import router as ingest_router
from app.routers.users import router as users_router
from app.routers.devices import router as devices_router
from app.routers.events import router as events_router
from app.routers.incidents import router as incidents_router
from app.routers.alerts import router as alerts_router
from app.routers.confirmations import router as confirmations_router

app = FastAPI(title="Safety Detection API (FastAPI)")

# 전역 예외 핸들러
@app.exception_handler(IntegrityError)
async def handle_integrity_error(request: Request, exc: IntegrityError):
    return JSONResponse(status_code=400, content={"ok": False, "error": "Database integrity error"})

@app.exception_handler(Exception)
async def handle_exception(request: Request, exc: Exception):
    print("UNHANDLED:", repr(exc))
    return JSONResponse(status_code=500, content={"ok": False, "error": "Internal Server Error"})

# 라우터 연결
app.include_router(health_router)
app.include_router(ingest_router)
app.include_router(users_router)
app.include_router(devices_router)
app.include_router(events_router)
app.include_router(incidents_router)
app.include_router(alerts_router)
app.include_router(confirmations_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=PORT, reload=True)
