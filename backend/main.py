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

app.include_router(wallet.router, prefix="/wallet", tags=["Wallet"])
app.include_router(opportunities.router, prefix="/opportunities", tags=["Opportunities"])
app.include_router(briefings.router, prefix="/briefings", tags=["Briefings"])
app.include_router(copilot.router, prefix="/copilot", tags=["Copilot"])


@app.get("/health")
def health():
    return {"status": "ok"}
