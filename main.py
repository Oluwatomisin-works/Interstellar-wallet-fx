from fastapi import FastAPI
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


wallets = {}


FX_RATES = {
    ("USDx", "cNGN"): 1495.0,
    ("cNGN", "USDx"): 1/1495.0,
    ("USDx", "EURx"): 0.84,
    ("EURx", "USDx"): 1/0.84,
    ("EURx", "cNGN"): 1779.1,
    ("cNGN", "EURx"): 1/1779.1,
}


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


@app.get("/")
def read_root():
    return {"message": "Backend Ti'n Sise"}


@app.post("/wallets")
def create_wallet():
    wallet_id = str(uuid.uuid4())
    wallets[wallet_id] = {
        "balances": {
            "USDx": 0.0,
            "EURx": 0.0,
            "cNGN": 0.0,
            "cXAF": 0.0
            }
    }
    return {
        "wallet_id": wallet_id,
        "balances": wallets[wallet_id]["balances"]
    }

@app.post("/deposit")
def deposit_funds(data: DepositRequest):
    if data.wallet_id not in wallets:
        return {"error": "Wallet not found"}
    if data.amount <= 0:
        return {"error": "Amount must be greater than zero"}
    if data.currency not in wallets[data.wallet_id]["balances"]:
        return {"error": "Unsupported currency"}

    wallets[data.wallet_id]["balances"][data.currency] += data.amount
    return {
        "wallet_id": data.wallet_id,
        "balances": wallets[data.wallet_id]["balances"]
    }

@app.post("/swap")
def swap_currency(data: SwapRequest):
    if data.wallet_id not in wallets:
        return {"error": "Wallet not found"}

    balances = wallets[data.wallet_id]["balances"]

    if data.from_currency not in balances or data.to_currency not in balances:
        return {"error": "Unsupported currency"}
    if data.amount <= 0:
        return {"error": "Amount must be greater than zero"}
    if balances[data.from_currency] < data.amount:
        return {"error": "Insufficient funds"}


    rate = FX_RATES.get((data.from_currency, data.to_currency))

    if rate is None:
        return {"error": "FX pair is not supported"}
    converted_amount = data.amount * rate

    balances[data.from_currency] -= data.amount
    balances[data.to_currency] += converted_amount

    return {
        "status": "success",
        "from_currency": data.from_currency,
        "to_currency": data.to_currency,
        "rate": rate,
        "converted_amount": converted_amount,
        "balances": balances
    }

@app.post("/transfer")
def transfer_funds(data: TransferRequest):
    if data.from_wallet not in wallets or data.to_wallet not in wallets:
        return {"error": "Wallet not found"}
    if data.amount <= 0:
        return {"error": "Amount must be greater than zero"}
    from_balances = wallets[data.from_wallet]["balances"]
    to_balances = wallets[data.to_wallet]["balances"]

    if data.currency not in from_balances:
        return {"error": "Unsupported currency"}
    if from_balances[data.currency] < data.amount:
        return {"error": "Insufficient funds"}
    from_balances[data.currency] -= data.amount
    to_balances[data.currency] += data.amount

    return {
        "from_wallet": data.from_wallet,
        "to_wallet": data.to_wallet,
        "currency": data.currency,
        "amount": data.amount,
    }

@app.get("/wallet/{wallet_id}")
def get_wallet(wallet_id: str):
    if wallet_id not in wallets:
        return {"error": "Wallet not found"}

    return {
        "wallet_id": wallet_id,
        "balances": wallets[wallet_id]["balances"]
    }