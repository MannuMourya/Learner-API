from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
from pathlib import Path
from loguru import logger

from app.core.config import settings
from app.api.deps import get_current_user

router = APIRouter(prefix="/files", tags=["files"])

UPLOAD_DIR = Path(settings.DATA_DIR) / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload")
async def upload_file(f: UploadFile = File(...), user=Depends(get_current_user)):
    # Simple content type whitelist (extend as desired)
    allowed = {"text/plain", "image/png", "image/jpeg", "application/pdf"}
    if f.content_type not in allowed:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    dest = UPLOAD_DIR / f.filename
    i = 1
    # Avoid overwriting
    while dest.exists():
        dest = UPLOAD_DIR / f"{Path(f.filename).stem}_{i}{Path(f.filename).suffix}"
        i += 1
    contents = await f.read()
    dest.write_bytes(contents)
    logger.info(f"Uploaded file {dest.name} by user {user.email}")
    return {"filename": dest.name, "size": len(contents), "content_type": f.content_type}

@router.get("/{filename}")
def get_file(filename: str, user=Depends(get_current_user)):
    path = UPLOAD_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path)
