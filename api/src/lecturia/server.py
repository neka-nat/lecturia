from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .router import router

app = FastAPI()
app.include_router(router, prefix="/api")

RESULTS_DIR = Path(__file__).resolve().parents[2] / "results"
app.mount("/results", StaticFiles(directory=str(RESULTS_DIR)), name="results")
