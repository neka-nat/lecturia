import os
import urllib.parse

from fastapi import FastAPI, Path, status
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from .router import router

app = FastAPI()

origins_env = os.getenv("CORS_ALLOWED_ORIGINS", "")
origins = [o.strip() for o in origins_env.split(",") if o.strip()]
if not origins:
    origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

if os.getenv("STORAGE_EMULATOR_HOST"):
    BASE_URL = f"http://localhost:4443/storage/v1/b/{os.getenv('GOOGLE_CLOUD_STORAGE_PUBLIC_BUCKET_NAME')}/o"
else:
    BASE_URL = f"https://storage.googleapis.com/{os.getenv('GOOGLE_CLOUD_STORAGE_PUBLIC_BUCKET_NAME')}"


@app.get("/")
async def root():
    return {"message": "Hello, World!"}


@app.get("/health")
async def health():
    return {"message": "OK"}


@app.get("/static/{full_path:path}")
async def static_redirect(full_path: str = Path(..., description="ex. css/app.css")):
    # パス traversal 対策
    safe_path = urllib.parse.quote(full_path.lstrip("/"), safe=":/~!@$&()*+,;=")
    url = f"{BASE_URL}/{safe_path}"
    if os.getenv("STORAGE_EMULATOR_HOST"):
        url += "?alt=media"
    logger.info(f"Redirecting to {url}")
    return RedirectResponse(url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
