"""
backend/main.py — Syn Bank SoW Intelligence Engine API
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import wallet, opportunities, briefings, copilot


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pre-warm the model cache on startup so the first HTTP request is fast.
    from models.opportunity_engine import build_scored_dataset
    from models.explainability import add_explainability_fields
    add_explainability_fields(build_scored_dataset())
    yield


app = FastAPI(title="Syn Bank SoW Intelligence Engine", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-project.vercel.app",  # we will replace with your actual Vercel URL-if we deploy to Vercel
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(wallet.router, tags=["Wallet"])
app.include_router(opportunities.router, tags=["Opportunities"])
app.include_router(briefings.router, tags=["Briefings"])
app.include_router(copilot.router, tags=["Copilot"])


@app.get("/health")
def health():
    return {"status": "ok"}
