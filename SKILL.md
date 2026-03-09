---
name: bityield
description: BTC and equity options volatility trading knowledge base, centered on the BitYield strategy framework. Use when the user mentions options, vol surface, skew trading, kurtosis, Risk Reversal, Butterfly, Delta hedging, implied volatility, Vega, Vanna, or asks to analyze/trade options on BTC, NVDA, AAPL, TSLA, META, AMZN, MSFT, GOOGL or any other ticker. Triggers include 期权 (options), Vol Surface, RR, skew, skewness, kurtosis, BitYield, Baowin, volatility arbitrage, sell put, iron condor, straddle, strangle, butterfly spread, options P&L.
---

# Options Volatility Trading (BitYield Framework)

## Core Framework

Three-dimensional volatility decomposition: **Variance** · **Skewness** · **Kurtosis**

**BitYield insight:** Minimize variance exposure; systematically harvest skewness + kurtosis premiums.

Reference files:
- **[strategy-core.md](references/strategy-core.md)** — Strategy logic, instruments, backtest data, prerequisites skill tree
- **[vol-surface-guide.md](references/vol-surface-guide.md)** — Vol Surface construction, Smile Delta, Vanna/Volga management, position entry workflow

## Live Data

Fetch real-time BTC Vol Surface and trading signals:

```bash
python3 ~/.openclaw/workspace/skills/btc-vol-trading/scripts/fetch_vol_surface.py
```

For equities (NVDA, AAPL, TSLA, etc.) use `yfinance` with `lastPrice` + custom IV solver (see `references/vol-surface-guide.md` §7).

**Signal thresholds:**
- 25d RR < -10%: Put Skew steep → strong RR opportunity (sell OTM Put / buy OTM Call)
- 25d RR < -5%: Moderate skew premium → standard RR entry
- 25d RR > -2%: Skew compressed → wait or reduce size
- 25d BF > 2%: Kurtosis premium rich → layer Butterfly on top of RR

## Common Tasks

**Scan skew opportunities across tickers:**
Fetch ATM IV, 25d RR, 25d BF for a basket of equities; rank by |RR| and BF simultaneously.

**Build an RR position:**
Run `fetch_vol_surface.py` (BTC) or yfinance (equities) → identify 25d strikes → calculate net premium, Greeks, hedge ratio, and P&L scenarios per `vol-surface-guide.md` §6.

**Layer Butterfly (kurtosis overlay):**
Add: Sell OTM Strangle (wings) + Buy ATM Straddle (body). Cost vs. Theta trade-off: sacrifices daily decay in exchange for tail protection — use when BF > 2% or ahead of binary events.

**Evaluate BitYield strategy:**
Read `strategy-core.md` for full version history (V1→V4), backtest metrics, and prerequisites skill tree.

## Dependencies
```bash
pip install requests scipy yfinance
```
