from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette_exporter import PrometheusMiddleware, handle_metrics
from loguru import logger
from time import time

from app.core.config import settings
from app.api.routes import auth, items, files, utils

# Simple in-memory rate limiter: N requests per window per IP
class RateLimiter(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int, window_seconds: int):
        super().__init__(app)
        self.max = max_requests
        self.window = window_seconds
        self.store: dict[str, tuple[int, float]] = {}

    async def dispatch(self, request: Request, call_next):
        ip = request.client.host if request.client else "unknown"
        now = time()
        count, reset = self.store.get(ip, (0, now + self.window))
        if now > reset:
            count, reset = 0, now + self.window
        count += 1
        self.store[ip] = (count, reset)
        if count > self.max:
            return JSONResponse({"detail": "Rate limit exceeded"}, status_code=429)
        return await call_next(request)

app = FastAPI(title=settings.APP_NAME)

# Middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS if settings.ALLOWED_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimiter, max_requests=settings.RATE_LIMIT_REQ, window_seconds=settings.RATE_LIMIT_WINDOW_SECONDS)
app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", handle_metrics)

# Routers
app.include_router(auth.router)
app.include_router(items.router)
app.include_router(files.router)
app.include_router(utils.router)

# Global error handler example
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception(exc)
    return JSONResponse({"detail": "Internal Server Error"}, status_code=500)
