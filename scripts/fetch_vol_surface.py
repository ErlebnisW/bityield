#!/usr/bin/env python3
"""
BTC Vol Surface 数据抓取器
从 Deribit 免费 API 抓取当前 BTC 期权链，计算关键指标

用法：python fetch_vol_surface.py [--expiry YYYY-MM-DD]
"""
import json, requests, sys
from datetime import datetime, timezone
from math import log, sqrt, exp
from scipy.stats import norm

BASE = "https://www.deribit.com/api/v2/public"

def get_btc_price():
    r = requests.get(f"{BASE}/get_index_price", params={"index_name": "btc_usd"}, timeout=10)
    return r.json()["result"]["index_price"]

def get_option_chain(currency="BTC"):
    r = requests.get(f"{BASE}/get_book_summary_by_currency",
                     params={"currency": currency, "kind": "option"}, timeout=15)
    return r.json()["result"]

def parse_instrument(name):
    """解析 BTC-8MAR25-80000-C 格式"""
    parts = name.split("-")
    if len(parts) != 4:
        return None
    return {
        "expiry_str": parts[1],
        "strike": float(parts[2]),
        "type": "call" if parts[3] == "C" else "put"
    }

def black_scholes_delta(S, K, T, r, sigma, opt_type):
    if T <= 0 or sigma <= 0:
        return 0
    d1 = (log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*sqrt(T))
    if opt_type == "call":
        return norm.cdf(d1)
    else:
        return norm.cdf(d1) - 1

def get_expiries():
    chain = get_option_chain()
    expiries = set()
    for opt in chain:
        info = parse_instrument(opt["instrument_name"])
        if info:
            expiries.add(info["expiry_str"])
    return sorted(expiries)

def analyze_expiry(chain, S, expiry_str):
    """分析某到期日的 Vol Smile，计算 ATM / 25d RR / 25d BF"""
    opts = []
    for opt in chain:
        info = parse_instrument(opt["instrument_name"])
        if not info or info["expiry_str"] != expiry_str:
            continue
        iv = opt.get("mark_iv", 0)
        if not iv or iv <= 0:
            continue
        # 计算到期时间
        try:
            exp_dt = datetime.strptime(expiry_str, "%d%b%y").replace(tzinfo=timezone.utc)
            T = (exp_dt.timestamp() - datetime.now(timezone.utc).timestamp()) / (365.25 * 86400)
        except:
            T = 0.05
        if T <= 0:
            continue
        delta = black_scholes_delta(S, info["strike"], T, 0, iv/100, info["type"])
        opts.append({
            "strike": info["strike"],
            "type": info["type"],
            "iv": iv,
            "delta": abs(delta),
            "T": T,
        })

    if not opts:
        return None

    # 找 ATM
    atm_calls = [o for o in opts if o["type"] == "call"]
    atm_call = min(atm_calls, key=lambda x: abs(x["strike"] - S)) if atm_calls else None
    atm_iv = atm_call["iv"] if atm_call else None

    # 找 25-delta
    calls_25 = min([o for o in opts if o["type"] == "call" and o["delta"] > 0.1],
                   key=lambda x: abs(x["delta"] - 0.25), default=None)
    puts_25  = min([o for o in opts if o["type"] == "put"  and o["delta"] > 0.1],
                   key=lambda x: abs(x["delta"] - 0.25), default=None)

    rr_25 = None
    bf_25 = None
    if calls_25 and puts_25 and atm_iv:
        rr_25 = calls_25["iv"] - puts_25["iv"]
        bf_25 = (calls_25["iv"] + puts_25["iv"]) / 2 - atm_iv

    return {
        "expiry": expiry_str,
        "atm_iv": atm_iv,
        "rr_25": rr_25,
        "bf_25": bf_25,
        "calls_25_iv": calls_25["iv"] if calls_25 else None,
        "puts_25_iv":  puts_25["iv"]  if puts_25  else None,
        "T_days": int((opts[0]["T"] if opts else 0) * 365.25),
    }

def skew_signal(rr_25, bf_25):
    signals = []
    if rr_25 is not None:
        if rr_25 < -8:
            signals.append("⚠️ Put Skew 极度陡峭，市场恐慌，RR 溢价丰厚")
        elif rr_25 < -4:
            signals.append("✅ Put Skew 正常偏高，适合建 RR（卖Put/买Call）")
        elif rr_25 > -2:
            signals.append("⚡ Skew 压缩，RR 溢价薄，谨慎建仓")
        else:
            signals.append("📊 Skew 中性区间")
    if bf_25 is not None:
        if bf_25 > 2.5:
            signals.append("✅ 峰度溢价丰厚，适合叠加 Butterfly")
        elif bf_25 > 1:
            signals.append("📊 峰度溢价正常")
        else:
            signals.append("⚡ 峰度溢价偏低")
    return signals

def main():
    print("📡 获取 BTC 实时价格...")
    S = get_btc_price()
    print(f"   BTC: ${S:,.0f}")

    print("\n📡 获取期权链...")
    chain = get_option_chain()
    print(f"   共 {len(chain)} 个合约")

    expiries = get_expiries()
    target_expiries = expiries[:5]  # 取最近 5 个到期日

    print(f"\n📊 Vol Surface 分析")
    print("=" * 65)
    print(f"{'到期日':12} {'DTE':>5} {'ATM IV':>8} {'25d RR':>8} {'25d BF':>8}")
    print("-" * 65)

    results = []
    for exp in target_expiries:
        r = analyze_expiry(chain, S, exp)
        if r:
            results.append(r)
            atm = f"{r['atm_iv']:.1f}%" if r['atm_iv'] else "N/A"
            rr  = f"{r['rr_25']:+.1f}%" if r['rr_25'] is not None else "N/A"
            bf  = f"{r['bf_25']:+.1f}%" if r['bf_25'] is not None else "N/A"
            print(f"{r['expiry']:12} {r['T_days']:>5}d {atm:>8} {rr:>8} {bf:>8}")

    print("=" * 65)

    # 最近到期日的信号
    if results:
        near = results[0]
        print(f"\n🎯 最近到期日（{near['expiry']}）交易信号：")
        for sig in skew_signal(near["rr_25"], near["bf_25"]):
            print(f"   {sig}")

if __name__ == "__main__":
    main()
