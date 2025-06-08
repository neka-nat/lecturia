import urllib.parse

from fastapi import FastAPI, Path, status
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from .router import router

app = FastAPI()

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

BASE_URL = "http://localhost:4443/storage/v1/b/lecturia-public-storage/o"

@app.get("/static/{full_path:path}")
async def static_redirect(full_path: str = Path(..., description="ex. css/app.css")):
    # パス traversal 対策
    safe_path = urllib.parse.quote(full_path.lstrip("/"), safe=":/~!@$&()*+,;=")
    url = f"{BASE_URL}/{safe_path}?alt=media"
    logger.info(f"Redirecting to {url}")
    return RedirectResponse(url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
