import { useEffect, useState } from "react";
import "./App.css";

const API = "https://klyf46-8000.csb.app";

const CURRENCIES = ["USDx", "EURx", "cNGN", "cXAF"];

export default function App() {
    const [wallet, setWallet] = useState("");
    const [lookupWallet, setLookupWallet] = useState("");
    const [balances, setBalances] = useState({});
    const [txs, setTxs] = useState([]);

    const [depositAmount, setDepositAmount] = useState("");
    const [depositCurrency, setDepositCurrency] = useState("USDx");

    const [swapAmount, setSwapAmount] = useState("");
    const [fromCur, setFromCur] = useState("USDx");
    const [toCur, setToCur] = useState("EURx");

    const [transferAmount, setTransferAmount] = useState("");
    const [transferCurrency, setTransferCurrency] = useState("USDx");
    const [toWallet, setToWallet] = useState("");

    const [error, setError] = useState("");
    const [theme, setTheme] = useState("light");

    function isValidNumber(value) {
        return value !== "" && !isNaN(value);
    }

    async function refresh(w = wallet) {
        if (!w) return;

        const res = await fetch(`${API}/wallets/${w}`);
        const data = await res.json();

        setBalances(data.balances || {});
        setTxs(data.transactions || []);
    }

    async function createWallet() {
        setError("");
        const res = await fetch(`${API}/wallets`, { method: "POST" });
        const data = await res.json();
        setWallet(data.wallet_id);
        setBalances({});
        setTxs([]);
    }

    async function deposit() {
        if (!isValidNumber(depositAmount)) {
            setError("Amount must be numeric.");
            return;
        }

        await fetch(`${API}/deposit`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                wallet_id: wallet,
                currency: depositCurrency,
                amount: Number(depositAmount)
            })
        });

        refresh();
    }

    async function swap() {
        if (!isValidNumber(swapAmount)) {
            setError("Amount must be numeric.");
            return;
        }

        await fetch(`${API}/swap`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                wallet_id: wallet,
                from_currency: fromCur,
                to_currency: toCur,
                amount: Number(swapAmount)
            })
        });

        refresh();
    }

    async function transfer() {
        if (!isValidNumber(transferAmount)) {
            setError("Amount must be numeric.");
            return;
        }

        await fetch(`${API}/transfer`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                from_wallet: wallet,
                to_wallet: toWallet,
                currency: transferCurrency,
                amount: Number(transferAmount)
            })
        });

        refresh();
    }

    async function lookup() {
        refresh(lookupWallet);
    }

    return (
        <div className={`app ${theme}`}>
            <h1 className="title">InterPockt</h1>

            <label>Background Mode</label>
            <select onChange={(e) => setTheme(e.target.value)}>
                <option value="light">Light</option>
                <option value="dark">Dark</option>
                <option value="blue">Blue</option>
            </select>

            <hr />

            <button onClick={createWallet}>Create Wallet</button>
            <p><b>Wallet ID:</b> {wallet}</p>

            {error && <p className="error">{error}</p>}

            <h3>Balances</h3>
            <ul>
                {Object.entries(balances).map(([c, v]) => (
                    <li key={c}>{c}: {v}</li>
                ))}
            </ul>

            <h3>Deposit</h3>
            <label>Amount</label>
            <input value={depositAmount} onChange={e => setDepositAmount(e.target.value)} />
            <label>Currency</label>
            <select value={depositCurrency} onChange={e => setDepositCurrency(e.target.value)}>
                {CURRENCIES.map(c => <option key={c}>{c}</option>)}
            </select>
            <button onClick={deposit}>Deposit</button>

            <h3>Swap</h3>
            <label>Amount</label>
            <input value={swapAmount} onChange={e => setSwapAmount(e.target.value)} />
            <label>From</label>
            <select value={fromCur} onChange={e => setFromCur(e.target.value)}>
                {CURRENCIES.map(c => <option key={c}>{c}</option>)}
            </select>
            <label>To</label>
            <select value={toCur} onChange={e => setToCur(e.target.value)}>
                {CURRENCIES.map(c => <option key={c}>{c}</option>)}
            </select>
            <button onClick={swap}>Swap</button>

            <h3>Transfer</h3>
            <label>Amount</label>
            <input value={transferAmount} onChange={e => setTransferAmount(e.target.value)} />
            <label>Currency</label>
            <select value={transferCurrency} onChange={e => setTransferCurrency(e.target.value)}>
                {CURRENCIES.map(c => <option key={c}>{c}</option>)}
            </select>
            <input placeholder="To Wallet ID" value={toWallet} onChange={e => setToWallet(e.target.value)} />
            <button onClick={transfer}>Transfer</button>

            <h3>Lookup Wallet</h3>
            <input value={lookupWallet} onChange={e => setLookupWallet(e.target.value)} />
            <button onClick={lookup}>Fetch Wallet</button>

            <h3>Transactions</h3>
            {txs.length === 0 ? <p>No transactions yet.</p> :
                <ul>
                    {txs.map((tx, i) => (
                        <li key={i}>{tx.type} — {tx.amount} {tx.currency}</li>
                    ))}
                </ul>
            }
        </div>
    );
}