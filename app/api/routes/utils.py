from fastapi import APIRouter, Depends, BackgroundTasks, Query
from fastapi import WebSocket, WebSocketDisconnect
from time import sleep
from loguru import logger
from datetime import datetime
from app.api.deps import get_current_user, require_admin

router = APIRouter(tags=["utils"])

@router.get("/health")
def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat() + "Z"}

@router.get("/echo")
def echo(message: str = Query("hello")):
    return {"echo": message}

@router.get("/whoami")
def whoami(user=Depends(get_current_user)):
    return {"id": user.id, "email": user.email, "role": user.role}

@router.get("/admin/stats")
def admin_stats(admin=Depends(require_admin)):
    # A trivial admin-protected endpoint
    return {"users": "redacted", "server": "running"}

@router.post("/tasks/heavy", status_code=202)
def heavy_task(background: BackgroundTasks, user=Depends(get_current_user)):
    def run():
        logger.info(f"Started heavy task for {user.email}")
        sleep(2)
        logger.info("Heavy task complete")
    background.add_task(run)
    return {"status": "queued"}

# WebSocket Echo
@router.websocket("/ws/echo")
async def websocket_echo(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            msg = await ws.receive_text()
            await ws.send_text(msg)
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
