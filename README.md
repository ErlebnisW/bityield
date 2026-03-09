# btc-vol-trading — Options Volatility Skill (BitYield Framework)

An OpenClaw agent skill for analyzing and trading options volatility using the **BitYield** three-dimensional framework. Covers BTC options on Deribit and equity options (NVDA, AAPL, TSLA, META, AMZN, GOOGL, MSFT, etc.).

## What This Skill Does

- **Real-time Vol Surface analysis**: Fetch ATM IV, 25d Risk Reversal, 25d Butterfly across expiries
- **Multi-ticker skew scanner**: Rank equity options by skew and kurtosis premium simultaneously
- **Position calculator**: Entry price, net premium, Greeks (Delta/Gamma/Vega/Theta/Vanna), Delta hedge ratio, and P&L scenarios at expiry
- **Strategy explainer**: Full BitYield framework (Variance → Skewness → Kurtosis), backtest metrics, prerequisites skill tree

## Strategy Overview

BitYield decomposes options premium into three statistical moments and harvests each independently:

| Dimension | Instrument | Signal |
|-----------|------------|--------|
| Variance | Straddle | Avoid (unbounded in extremes) |
| **Skewness** | **Risk Reversal** | **25d RR < −5% → entry signal** |
| **Kurtosis** | **Butterfly** | **25d BF > 2% → layer on top** |

**Backtest performance (Aug 2025 – Feb 2026, including Oct/Feb extreme moves):**

| Version | Sharpe | Calmar | Max DD |
|---------|--------|--------|--------|
| Skew only | 1.24 | 3.50 | −1,169 |
| Skew + Kurtosis V1 | 3.47 | 7.79 | −1,003 |
| **Skew + Kurtosis V2** | **5.09** | **19.70** | **−750** |

## Skill Structure

```
btc-vol-trading/
├── SKILL.md                        # Agent trigger + workflow guide
├── README.md                       # This file
├── references/
│   ├── strategy-core.md            # BitYield strategy deep-dive
│   └── vol-surface-guide.md        # Vol Surface construction & operations
└── scripts/
    └── fetch_vol_surface.py        # Live BTC Vol Surface from Deribit API
```

## Quick Start

### BTC Vol Surface (live)
```bash
pip install requests scipy
python3 scripts/fetch_vol_surface.py
```

Sample output:
```
NVDA $177.82 — Vol Surface
Expiry       DTE   ATM IV    25d RR    25d BF
2026-04-17   38d    48.8%   -13.7%    +1.3%   ← Strong skew signal
2026-06-18  100d    49.3%   -10.0%    -0.4%
```

### Equity Options (via yfinance)
```bash
pip install yfinance scipy
```
Use `lastPrice` + `brentq` IV solver — pre-market `bid/ask` is always 0.

## Trigger Examples

This skill activates when you mention:
- Options analysis on any ticker ("analyze NVDA options")
- Vol Surface / skew / RR / Butterfly
- BitYield / Baowin strategy questions
- Greeks (Delta, Vega, Vanna, Volga)
- 期权 (Chinese: "options")

## Data Sources

| Source | Data | Cost |
|--------|------|------|
| Deribit API | BTC/ETH options chain, IV | Free |
| yfinance | Equity options chain | Free |
| alternative.me | Crypto Fear & Greed | Free |
| tardis.dev | Historical Vol Surface | Free (delayed) |

## References

- BitYield strategy: https://baowin.vercel.app/
- Intro slides: https://baowin-intro.pages.dev/
- Community: https://t.me/GlobalLife2023
