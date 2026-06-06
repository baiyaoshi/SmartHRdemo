# -*- coding: utf-8 -*-
"""FastAPI 主入口"""

from dotenv import load_dotenv
load_dotenv()

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.database import engine, Base
from backend.app.api import positions
from backend.app.api.resumes import router as resumes_router
from backend.app.api.match import router as match_router



@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Smart-HR API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(resumes_router, prefix="/api/hr/resumes", tags=["resumes"])
app.include_router(positions.router, prefix="/api/hr/positions", tags=["positions"])
app.include_router(match_router, prefix="/api/hr", tags=["match"])

@app.get("/")
def root():
    return {"message": "Smart-HR API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


"""
cd F:\develop\agent\SmartHRdemo
uv run uvicorn backend.app.main:app --reload --port 8080

"""