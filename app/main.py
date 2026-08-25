"""Rabitah API — FastAPI application entrypoint."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.core.config import get_settings
from app.core.database import Base, engine
from app.routers import analytics, auth, links, page

settings = get_settings()
limiter = Limiter(key_func=get_remote_address)

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Smart link-in-bio & micro-page builder for creators.",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(links.router)
app.include_router(page.router)
app.include_router(analytics.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/app")
def app_shell():
    return FileResponse(STATIC_DIR / "app.html")


@app.get("/app/{rest:path}")
def spa_fallback(rest: str):
    """Serve the SPA shell for client-side routes."""
    return FileResponse(STATIC_DIR / "app.html")


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
