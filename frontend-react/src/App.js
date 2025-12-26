import { useEffect, useState, useCallback } from "react";

const API = "http://127.0.0.1:8000";

function App() {
    const [wallet, setWallet] = useState("");
    const [balances, setBalances] = useState({});
    const [txs, setTxs] = useState([]);
    const [amount, setAmount] = useState("");
    const [currency, setCurrency] = useState("USDx");
    const [fromCur, setFromCur] = useState("USDx");
    const [toCur, setToCur] = useState("EURx");
    const [toWallet, setToWallet] = useState("");

    const refresh = useCallback(async () => {
        if (!wallet) {
            return;
        }

        const walletRes = await fetch(`${API}/wallets/${wallet}`);
        const walletData = await walletRes.json();
        setBalances(walletData.balances || {});

        const txRes = await fetch(`${API}/transactions`);
        const txData = await txRes.json();
        setTxs(txData);
    }, [wallet]);

    async function createWallet() {
        const res = await fetch(`${API}/wallets`, { method: "POST" });
        const data = await res.json();
        setWallet(data.wallet_id);
        setBalances({});
    }

    async function deposit() {
        await fetch(`${API}/deposit`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                wallet_id: wallet,
                currency: currency,
                amount: Number(amount)
            })
        });
        await refresh();
    }

    async function swap() {
        await fetch(`${API}/swap`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                wallet_id: wallet,
                from_currency: fromCur,
                to_currency: toCur,
                amount: Number(amount)
            })
        });
        await refresh();
    }

    async function transfer() {
        await fetch(`${API}/transfer`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                from_wallet: wallet,
                to_wallet: toWallet,
                currency: currency,
                amount: Number(amount)
            })
        });
        await refresh();
    }

    useEffect(() => {
        refresh();
    }, [refresh]);

    return (
        <div style={{ padding: 20 }}>
            <h1>Operation Borderless</h1>

            <button onClick={createWallet}>Create Wallet</button>
            <p><b>Wallet ID:</b> {wallet}</p>

            <h3>Balances</h3>
            <pre>{JSON.stringify(balances, null, 2)}</pre>

            <input
                placeholder="Amount"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
            />
            <input
                placeholder="Currency"
                value={currency}
                onChange={(e) => setCurrency(e.target.value)}
            />
            <button onClick={deposit}>Deposit</button>

            <br /><br />

            <input
                placeholder="From Currency"
                value={fromCur}
                onChange={(e) => setFromCur(e.target.value)}
            />
            <input
                placeholder="To Currency"
                value={toCur}
                onChange={(e) => setToCur(e.target.value)}
            />
            <button onClick={swap}>Swap</button>

            <br /><br />

            <input
                placeholder="To Wallet ID"
                value={toWallet}
                onChange={(e) => setToWallet(e.target.value)}
            />
            <button onClick={transfer}>Transfer</button>

            <h3>Transactions</h3>
            <pre>{JSON.stringify(txs, null, 2)}</pre>
        </div>
    );
}

export default App;