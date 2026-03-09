# Baowin/BitYield Strategy — Core Knowledge Base

## 1. Three-Dimensional Volatility Framework

Implied volatility (IV) decomposes into three statistical moments:

| Dimension | Moment | Meaning | Instrument |
|-----------|--------|---------|------------|
| Variance | 2nd | Overall IV level (parallel surface shift) | Straddle / Strangle |
| Skewness | 3rd | Vol Smile slope (which tail is pricier) | Risk Reversal (RR) |
| Kurtosis | 4th | Vol Smile curvature (fat-tail thickness) | Butterfly (BF) |

**Core Baowin Insight:**
- **Variance**: Can spike without a ceiling in extreme markets (unbounded short-vega risk)
- **Skewness + Kurtosis**: Bounded fluctuation range → persistent, extractable premium

---

## 2. Three Primary Instruments

### 2.1 Straddle — Trading Variance
- Structure: Buy (or sell) same-strike ATM Call + Put
- After Delta hedge: pure Vega / Gamma exposure
- Use: Directional bet on overall IV level
- Risk: Short straddle faces unlimited loss in black-swan events

### 2.2 Risk Reversal (RR) — Trading Skewness
- Structure: Sell OTM Put + Buy OTM Call (Delta-neutral)
- Crypto: Put Skew is persistently steep (left tail expensive) → selling Puts harvests ongoing premium
- Key metric: 25-delta RR = IV(25d Call) − IV(25d Put)
- Management: Smile Delta hedge + Vanna management

### 2.3 Butterfly (BF) — Trading Kurtosis
- Structure: Buy 1 lower strike + Sell 2 middle strikes + Buy 1 higher strike (or OTM Strangle vs ATM Straddle)
- When BF > 0 (wings expensive): Sell BF = Sell OTM Strangle + Buy ATM Straddle
- Key metric: 25-delta BF = [IV(25d Call) + IV(25d Put)] / 2 − IV(ATM)
- Adding BF lifted Sharpe from 1.24 → 3.47+ in Baowin backtests

---

## 3. Baowin Strategy Structure

**Composite position:**
1. **Core: Risk Reversal** — Sell expensive OTM Put + Buy OTM Call, Delta-neutral
2. **Overlay: Butterfly** — Optimize kurtosis exposure, significantly improves Sharpe
3. **Protection: Long Gamma** — Extreme-event buffer, trades Sharpe for tail safety
4. **Hedge: Dynamic Delta/Vanna** — Systematic re-hedging throughout position life

**Stated targets (public):**
- 25% annualized return (BTC-denominated), max drawdown 5%

---

## 4. Key Greeks

| Greek | Meaning | Relevance |
|-------|---------|-----------|
| Delta (Δ) | Option price change per $1 move in underlying | Directional risk; requires dynamic hedging |
| Vega (ν) | Option price change per 1% IV move | Volatility level exposure |
| Gamma (Γ) | Rate of Delta change w.r.t. underlying price | Convexity; Long Gamma = protection |
| Vanna | Delta sensitivity to IV / Vega sensitivity to price | Core management item for Skew trades |
| Volga | Vega sensitivity to IV (2nd-order Vega) | Core management item for Kurtosis trades |

---

## 5. Backtest Results (Baowin, Aug 2025 – Feb 2026)

| Version | Ann. Sharpe | Calmar | Max DD | Total Return |
|---------|-------------|--------|--------|--------------|
| Skew only (RR) | 1.24 | 3.50 | −1,169 | 1,774 |
| Skew + Kurtosis V1 | 3.47 | 7.79 | −1,003 | 3,596 |
| Skew + Kurtosis V2 | **5.09** | **19.70** | −750 | 6,801 |
| + Long Gamma protection | 2.53 | 7.91 | −3,086 | **11,242** |

- Win rate: 47–59% (most days underwater — requires patience)
- Stress test: BTC ±20% still provides sufficient time window for dynamic re-hedging

---

## 6. Prerequisites Skill Tree

Executing skew trades requires mastery of:
1. **Vol Surface construction** (SVI / SABR model fitting)
2. **Surface tangent derivatives** (accurate dIV/dK, dIV/dT)
3. **Smile Delta hedging** (Sticky Delta, not Sticky Strike)
4. **Vanna management** (time-effect + tail management)

---

## 7. Market Environment Signals

### When skew premium is rich:
- FUD / fear regime (steep Put Skew): OTM Puts priced aggressively
- Pre-event uncertainty (kurtosis spike): Both tails expensive simultaneously

### When to be cautious:
- Post-vol-crush (IV compressed): Premium too thin to justify risk
- Active variance spike (IV surging): RR exposure hard to hedge cleanly

---

## 8. Deribit Operational Notes (BTC)

- Primary BTC options venue: Deribit (dominant), OKX, Bybit
- Recommended expiries: Friday expirations (DTE 7/14/30) for best liquidity
- Strike selection: 25-delta OTM (standard RR entry points)
- Collateral: BTC-margined (BTC-denominated) — avoids fiat FX risk

---

## 9. Baowin Public Information

- Strategy details: https://baowin.vercel.app/
- Minimum subscription: 0.1 BTC (Matrixport custody) or $5M USD equivalent (Deribit SMA)
- Lock-up: 6 months; redemption notice: 6 months
- Community: https://t.me/GlobalLife2023
