from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------
# IN-MEMORY STORAGE
# --------------------
wallets = {}
transactions = []

SUPPORTED = {"USDx", "EURx", "cNGN", "cXAF"}

FX_RATES = {
    ("USDx", "cNGN"): 1495.0,
    ("cNGN", "USDx"): 1 / 1495.0,
    ("USDx", "EURx"): 0.84,
    ("EURx", "USDx"): 1 / 0.84,
    ("EURx", "cNGN"): 1779.1,
    ("cNGN", "EURx"): 1 / 1779.1,
    ("USDx", "cXAF"): 559.8,
    ("cXAF", "USDx"): 1 / 559.8,
    ("cNGN", "cXAF"): 1 / 2.59,
    ("cXAF", "cNGN"): 2.59,
    ("EURx", "cXAF"): 655.96,
    ("cXAF", "EURx"): 1 / 655.96,
}

# --------------------
# SCHEMAS
# --------------------
class DepositRequest(BaseModel):
    wallet_id: str
    currency: str
    amount: float

class SwapRequest(BaseModel):
    wallet_id: str
    from_currency: str
    to_currency: str
    amount: float

class TransferRequest(BaseModel):
    from_wallet: str
    to_wallet: str
    currency: str
    amount: float

# --------------------
# HELPERS
# --------------------
def validate_amount(amount):
    if not isinstance(amount, (int, float)):
        raise HTTPException(400, "Amount must be numeric")
    if amount <= 0:
        raise HTTPException(400, "Amount must be positive")

def validate_currency(currency):
    if currency not in SUPPORTED:
        raise HTTPException(400, f"Unsupported currency: {currency}")

# --------------------
# ROUTES
# --------------------
@app.post("/wallets")
def create_wallet():
    wallet_id = str(uuid.uuid4())
    wallets[wallet_id] = {}
    return {"wallet_id": wallet_id}

@app.get("/wallets/{wallet_id}")
def get_wallet(wallet_id: str):
    if wallet_id not in wallets:
        raise HTTPException(404, "Wallet not found")
    return {"wallet_id": wallet_id, "balances": wallets[wallet_id]}

@app.post("/deposit")
def deposit(req: DepositRequest):
    validate_amount(req.amount)
    validate_currency(req.currency)

    if req.wallet_id not in wallets:
        raise HTTPException(404, "Wallet not found")

    wallets[req.wallet_id][req.currency] = (
        wallets[req.wallet_id].get(req.currency, 0) + req.amount
    )

    transactions.append({
        "wallet_id": req.wallet_id,
        "type": "deposit",
        "currency": req.currency,
        "amount": req.amount
    })

    return {"status": "success"}

@app.post("/swap")
def swap(req: SwapRequest):
    validate_amount(req.amount)
    validate_currency(req.from_currency)
    validate_currency(req.to_currency)

    if req.wallet_id not in wallets:
        raise HTTPException(404, "Wallet not found")

    rate = FX_RATES.get((req.from_currency, req.to_currency))
    if not rate:
        raise HTTPException(400, "FX rate unavailable")

    balance = wallets[req.wallet_id].get(req.from_currency, 0)
    if balance < req.amount:
        raise HTTPException(400, "Insufficient balance")

    wallets[req.wallet_id][req.from_currency] -= req.amount
    wallets[req.wallet_id][req.to_currency] = (
        wallets[req.wallet_id].get(req.to_currency, 0) + req.amount * rate
    )

    transactions.append({
        "wallet_id": req.wallet_id,
        "type": "swap",
        "currency": f"{req.from_currency}->{req.to_currency}",
        "amount": req.amount
    })

    return {"status": "success"}

@app.post("/transfer")
def transfer(req: TransferRequest):
    validate_amount(req.amount)
    validate_currency(req.currency)

    if req.from_wallet not in wallets or req.to_wallet not in wallets:
        raise HTTPException(404, "Wallet not found")

    balance = wallets[req.from_wallet].get(req.currency, 0)
    if balance < req.amount:
        raise HTTPException(400, "Insufficient balance")

    wallets[req.from_wallet][req.currency] -= req.amount
    wallets[req.to_wallet][req.currency] = (
        wallets[req.to_wallet].get(req.currency, 0) + req.amount
    )

    transactions.append({
        "wallet_id": req.from_wallet,
        "type": "transfer",
        "currency": req.currency,
        "amount": req.amount
    })

    return {"status": "success"}

@app.get("/transactions/{wallet_id}")
def get_transactions(wallet_id: str):
    return [t for t in transactions if t["wallet_id"] == wallet_id]