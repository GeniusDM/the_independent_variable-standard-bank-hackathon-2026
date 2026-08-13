"""
backend/main.py — Syn Bank SoW Intelligence Engine API
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import wallet, opportunities, briefings, copilot

app = FastAPI(title="Syn Bank SoW Intelligence Engine", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
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
