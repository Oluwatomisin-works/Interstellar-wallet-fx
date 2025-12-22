This project is a full-stack wallet and FX system built for Interstellar Solutions.

## Features
- Wallet creation
- Deposit mock stablecoins
- Swap currencies using FX rates
- Transfer between wallets
- Minimal frontend demo

## Tech Stack
- Backend: FastAPI (Python)
- Frontend: HTML + JavaScript
- Storage: In-memory (no database)

## Supported Currencies
- USDx (mock USD)
- EURx (mock EUR)
- cNGN (mock NGN)
- cXAF (mock CFA)

## FX Rates
FX rates are mocked to keep behaviour deterministic and testable.

## Running the Backend
```bash
python -m venv venv
venv\Scripts\Activate
pip install fastapi uvicorn
python -m uvicorn main:app --reload