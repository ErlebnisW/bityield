# Vol Surface Operational Guide

## 1. What Is a Vol Surface

A Vol Surface is a 3D surface with **Strike (K)** and **Expiry (T)** as axes and **Implied Volatility (IV)** as the z-axis.

```
IV (%)
  ^
  |      *  *              <- OTM Put wing (left)
  |    *      *            <- ATM center
  |  *          *  *       <- OTM Call wing (right)
  +--------------------------> Strike / Delta
```

Each expiry generates one "smile curve" (Vol Smile).

---

## 2. Key Metrics

| Metric | Formula | Meaning |
|--------|---------|---------|
| ATM Vol | IV(ATM) | Overall volatility level |
| 25d RR | IV(25dC) − IV(25dP) | Skew direction and strength |
| 25d BF | [IV(25dC) + IV(25dP)] / 2 − IV(ATM) | Kurtosis / smile curvature |
| 10d RR | IV(10dC) − IV(10dP) | Extreme tail skew |
| 10d BF | [IV(10dC) + IV(10dP)] / 2 − IV(ATM) | Extreme tail kurtosis |

**Crypto market norms:**
- RR typically negative (Put Skew): left tail more expensive than right
- BF typically positive: both tails more expensive than center (leptokurtic distribution)
- During panic: RR more negative, BF higher

---

## 3. Sticky Strike vs Sticky Delta (Smile Delta)

**Sticky Strike:**
- Assumes IV at a given strike doesn't change when underlying moves
- Simpler but underestimates real skew impact

**Sticky Delta (Smile Delta):**
- When underlying moves, IV for the same Delta moves with it
- Baowin uses this approach
- More accurate but requires full surface recalculation

**In practice:** With Smile Delta hedging, Delta = BS Delta + Vanna × dIV/dS

---

## 4. Vanna Management

**Vanna = dDelta/dVol = dVega/dS**

When BTC/equity drops:
1. IV rises (strong negative correlation in crypto)
2. Positions with negative Vanna (e.g., Short Put): Delta becomes more negative
3. Requires additional short-selling to hedge → can amplify downward pressure

**Management approach:**
- Calculate portfolio total Vanna
- Hedge via OTM Calls or Long Delta positions
- Reduce Vanna exposure proactively before expected stress events

---

## 5. Volga

**Volga = dVega/dVol = 2nd-order Vega**

- Butterfly positions (long both wings) are naturally Long Volga
- Long Volga profits when IV itself is volatile (regardless of direction)
- Adding BF increases portfolio Volga → extracts kurtosis premium

---

## 6. Position Entry Workflow (RR + BF Composite)

### Step 1: Read Current Vol Surface
```
Fetch current options chain (Deribit for BTC, yfinance for equities):
- Select target expiry (recommend DTE 14–30)
- Read ATM Vol, 25d RR, 25d BF
```

### Step 2: Assess Skew State
```
25d RR < -10%  → Steep Put Skew, strong signal: build RR (Sell Put / Buy Call)
25d RR < -5%   → Moderate skew, standard entry
25d RR > -2%   → Skew compressed, wait or reduce
25d BF > 2%    → Kurtosis premium rich, layer Butterfly
```

### Step 3: Enter Position (Delta-Neutral)
```
1. Sell 25d OTM Put (harvest skew premium)
2. Buy 25d OTM Call (hedge Vanna)
3. Calculate portfolio Delta, hedge to ~0 using spot/futures
4. Optional BF overlay: Sell ATM Straddle + Buy OTM Strangle (net Long BF)
```

### Step 4: Daily Maintenance
```
- Recalculate Delta daily; hedge to within ±0.1 BTC (or ±10 equity shares)
- Monitor Vanna exposure; hedge when threshold breached
- Roll or close 1–2 days before expiry
```

---

## 7. Data Sources

| Data | Source | Notes |
|------|--------|-------|
| BTC option chain | `api.deribit.com/api/v2/public/get_book_summary_by_currency` | Free public API |
| BTC index price | `api.deribit.com/api/v2/public/get_index_price?index_name=btc_usd` | Real-time |
| Equity options | `yfinance` (Python) — use `lastPrice` + custom IV solver (pre-market: bid/ask = 0) | Free |
| Historical IV | tardis.dev (free tier has delay) | Vol Surface history |
| Fear & Greed Index | alternative.me/crypto/fear-and-greed-index/ | Sentiment reference |

**Important (equities, pre-market):** `yfinance` returns bid/ask = 0.0 before market open. Use `lastPrice` with `scipy.optimize.brentq` to solve for IV numerically.

```python
from scipy.optimize import brentq
iv = brentq(lambda s: bs_price(S, K, T, r, s, opt_type) - last_price, 0.01, 5.0)
```
