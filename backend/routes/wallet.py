from fastapi import APIRouter
from backend.schemas import ClientWallet

router = APIRouter()


@router.get("/", response_model=list[ClientWallet])
def get_all_wallets():
    """Returns wallet estimates for all 50 clients."""
    # TODO: load from processed/client_wallet_summary.csv
    return []


@router.get("/{client_id}", response_model=ClientWallet)
def get_client_wallet(client_id: str):
    """Returns wallet estimate for a single client."""
    # TODO: filter by client_id
    return {}
