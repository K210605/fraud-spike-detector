# Fraud Spike Detector — AI Risk Manager

An AI-powered fraud detection system that monitors transactions in near real-time, flags suspicious spikes using both statistical rules and machine learning, and explains *why* each transaction was flagged.

Built for Razorpay AI Buildathon — Track 2: AI Risk Manager

## Problem

Payment platforms process thousands of transactions per second. Fraud often appears as a sudden "spike" — such as stolen-card testing (many small rapid transactions) or a single unusually large transaction. Detecting these spikes quickly, and explaining the reasoning to a risk analyst, is critical for platforms like Razorpay.

## Solution

This system combines:
- **Statistical rules** — detects velocity spikes (too many transactions in a short window) and amount anomalies (transactions far above a user's typical spend)
- **Machine learning (Isolation Forest)** — an unsupervised model that scores every transaction for anomalous behaviour, catching patterns the rules alone would miss
- **Human-readable explanations** — every flagged transaction includes a plain-language reason, not just a score

The result is served through a live, app-style dashboard (with sign-in screen and sidebar navigation) that mimics a real internal risk-monitoring tool.

## Architecture

```
Synthetic Transaction Data (data.py)
        |
Rule-Based Detection (detector_rules.py) ---+
        |                                    +--> Combined Detection (detector_combined.py)
ML Detection (detector_ml.py) --------------+
        |
SQLite Database (database.py)
        |
FastAPI Backend (api.py)
        |
Live Dashboard (dashboard.html)
        ^
Live Transaction Simulator (simulate.py)
```

## Tech Stack

- **Backend:** Python, FastAPI, Uvicorn
- **ML:** scikit-learn (Isolation Forest)
- **Data:** Pandas, NumPy
- **Database:** SQLite
- **Frontend:** HTML, CSS, vanilla JavaScript, Chart.js

## Features

- Synthetic transaction generator with injected fraud patterns for testing
- Dual-layer detection: statistical rules + unsupervised ML
- Human-readable flag explanations (e.g. "rapid transactions", "unusually high amount", "ML anomaly pattern")
- REST API with endpoints for all transactions, flagged transactions, and summary stats
- App-style dashboard: sign-in screen, sidebar navigation, search, filtering, pagination, and a transaction detail modal
- Auto-refreshing UI (near real-time monitoring)
- Live transaction simulator that continuously generates new transactions, occasionally injecting fraud spikes
- Model evaluation against known ground truth (Precision, Recall, F1, Accuracy)

## Results

Evaluated against 26 known injected fraud transactions in a 2,026-transaction dataset:

| Metric | Score |
|---|---|
| Precision | 0.349 |
| Recall | 0.815 |
| F1 Score | 0.489 |
| Accuracy | 0.977 |

The system prioritizes **recall** — catching as much real fraud as possible — since a missed fraud case is typically far costlier than a false alarm.

## How to Run

1. Install dependencies:
   ```
   pip install pandas numpy scikit-learn fastapi uvicorn
   ```

2. Generate synthetic transaction data:
   ```
   python data.py
   ```

3. Start the backend API:
   ```
   python api.py
   ```

4. (Optional) Start the live simulator in a separate terminal, to see the dashboard update in near real-time:
   ```
   python simulate.py
   ```

5. Open `dashboard.html` in a browser and click "Sign In" on the demo login screen.

6. (Optional) Run the evaluation script to see model performance metrics:
   ```
   python evaluate.py
   ```

## Future Improvements

- Connect to a real payment gateway's transaction stream (e.g. via webhooks) instead of simulated data
- Replace polling-based updates with WebSockets for true real-time push updates
- Add real user authentication and role-based access for a production deployment
- Expand the ML layer with supervised models once labeled fraud data is available

## Author

Khushi Sehgal — B.Tech CSE (Cybersecurity & Privacy)
