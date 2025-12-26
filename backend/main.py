from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pydantic import BaseModel, Field
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import uuid
import time

app = FastAPI(title="Operation Borderless API")

# --------------------
# CORS (Frontend access)
# --------------------
app.add_middleware( 
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Validation Error Handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"error": "Invalid input. Amount must be a numeric value"},
    )

# --------------------
# In-memory storage (prototype)
# --------------------
wallets = {}
transactions = []

# --------------------
# Models
# --------------------
class DepositRequest(BaseModel):
    wallet_id: str
    currency: str
    amount: float = Field(..., gt=0)

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
# Mock FX rates
# --------------------
FX_RATES = {
    ("USDx", "cNGN"): 1495.0,
    ("cNGN", "USDx"): 1/1495.0,
    ("USDx", "EURx"): 0.84,
    ("EURx", "USDx"): 1/0.84,
    ("EURx", "cNGN"): 1779.1,
    ("cNGN", "EURx"): 1/1779.1,
}

# --------------------
# Routes
# --------------------
@app.post("/wallets")
def create_wallet():
    wallet_id = str(uuid.uuid4())
    wallets[wallet_id] = {"balances": {}}
    return {"wallet_id": wallet_id}

@app.get("/wallets/{wallet_id}")
def get_wallet(wallet_id: str):
    if wallet_id not in wallets:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return wallets[wallet_id]

@app.post("/deposit")
def deposit(req: DepositRequest):
    if req.wallet_id not in wallets:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount")
    
    balances = wallets[req.wallet_id]["balances"]
    balances[req.currency] = balances.get(req.currency, 0) + req.amount
    
    transactions.append({
        "type": "deposit",
        "wallet": req.wallet_id,
        "currency": req.currency,
        "amount": req.amount,
        "timestamp": time.time()
        
    })
    
    return {"balances": balances}

@app.post("/swap")
def swap(req: SwapRequest):
    if req.wallet_id not in wallets:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    balances = wallets[req.wallet_id]["balances"]
    
    if balances.get(req.from_currency, 0) < req.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    rate = FX_RATES.get((req.from_currency, req.to_currency))
    if not rate:
        raise HTTPException(status_code=400, detail="FX rate unavailable")
    
    balances[req.from_currency] -= req.amount
    balances[req.to_currency] = balances.get(req.to_currency, 0) + req.amount * rate
    
    transactions.append({
        "type": "swap",
        "wallet": req.wallet_id,
        "from": req.from_currency,
        "to": req.to_currency,
        "amount": req.amount,
        "rate": rate,
        "timestamp": time.time()
    })
    
    return {"balances": balances}

@app.post("/transfer")
def transfer(req: TransferRequest):
    if req.from_wallet not in wallets or req.to_wallet not in wallets:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    from_bal = wallets[req.from_wallet]["balances"]
    to_bal = wallets[req.to_wallet]["balances"]
    
    if from_bal.get(req.currency, 0) < req.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    from_bal[req.currency] -= req.amount
    to_bal[req.currency] = to_bal.get(req.currency, 0) + req.amount
    
    transactions.append({
        "type": "transfer",
        "from": req.from_wallet,
        "to": req.to_wallet,
        "currency": req.currency,
        "amount": req.amount,
        "timestamp": time.time()
    })
    
    return {"status": "ok"}

@app.get("/transactions")
def get_transactions():
    return transactions