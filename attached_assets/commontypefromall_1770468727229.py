import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Nifty 50 stock symbols
nifty50_symbols = [
    "ADANIPORTS.NS", "ASIANPAINT.NS", "AXISBANK.NS", "BAJAJ-AUTO.NS", "BAJFINANCE.NS",
    "BAJAJFINSV.NS", "BPCL.NS", "BHARTIARTL.NS", "BRITANNIA.NS", "CIPLA.NS",
    "COALINDIA.NS", "DIVISLAB.NS", "DRREDDY.NS", "EICHERMOT.NS", "GRASIM.NS",
    "HCLTECH.NS", "HDFCBANK.NS", "HDFCLIFE.NS", "HEROMOTOCO.NS", "HINDALCO.NS",
    "HINDUNILVR.NS", "ICICIBANK.NS", "INDUSINDBK.NS", "INFY.NS", "ITC.NS",
    "JSWSTEEL.NS", "KOTAKBANK.NS", "LT.NS", "M&M.NS", "MARUTI.NS",
    "NESTLEIND.NS", "NTPC.NS", "ONGC.NS", "POWERGRID.NS", "RELIANCE.NS",
    "SBILIFE.NS", "SBIN.NS", "SHREECEM.NS", "SUNPHARMA.NS", "TATACONSUM.NS",
    "TATAMOTORS.NS", "TATASTEEL.NS", "TCS.NS", "TECHM.NS", "TITAN.NS",
    "ULTRACEMCO.NS", "UPL.NS", "WIPRO.NS"
]

# ---------- TIMEFRAME CONFIGURATION ----------
TIMEFRAMES = {
    'daily': {
        'interval': '1d',
        'period_scan': '1y',
        'period_single': '2y',
        'period_compare': '6mo',
        'sma_short': 20,
        'sma_long': 50,
        'name': 'DAILY'
    },
    'weekly': {
        'interval': '1wk',
        'period_scan': '2y',
        'period_single': '3y',
        'period_compare': '6mo',
        'sma_short': 10,
        'sma_long': 25,
        'name': 'WEEKLY'
    },
    'monthly': {
        'interval': '1mo',
        'period_scan': '5y',
        'period_single': '7y',
        'period_compare': '12mo',
        'sma_short': 6,
        'sma_long': 12,
        'name': 'MONTHLY'
    }
}

# ---------- RSI helper ----------
def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    rs = avg_gain / avg_loss
    rsi_val = 100 - (100 / (1 + rs))
    return rsi_val

# ---------- MACD helper (12,26,9) ----------
def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    hist = macd_line - signal_line
    return macd_line, signal_line, hist

# ---------- RSI+MACD text classifier ----------
def classify_rsi_macd_scenario(latest_rsi: float, macd_val: float, hist_slope: float) -> str:
    if pd.isna(latest_rsi) or pd.isna(macd_val) or pd.isna(hist_slope):
        return "Scenario: Not enough data."

    if 55 <= latest_rsi <= 70 and macd_val > 0 and hist_slope > 0:
        return "Scenario: Strong Bullish (long build – strong buy zone)."
    if 40 <= latest_rsi < 55 and macd_val > 0 and abs(hist_slope) < 0.05:
        return "Scenario: Short covering / weak rally (buy with caution)."
    if 60 <= latest_rsi <= 75 and macd_val > 0 and abs(hist_slope) < 0.1:
        return "Scenario: Quiet accumulation (buy setup valid)."
    if 45 <= latest_rsi <= 60 and macd_val > 0 and hist_slope < 0:
        return "Scenario: Profit-taking or early reversal (partial exit)."
    if 20 <= latest_rsi <= 40 and macd_val < 0 and hist_slope < 0:
        return "Scenario: Strong Bearish (short build – strong sell bias)."
    if 20 <= latest_rsi <= 35 and macd_val < 0 and hist_slope > 0:
        return "Scenario: Liquidation / panic washout (shorts covering)."
    if 30 <= latest_rsi <= 50 and macd_val < 0 and abs(hist_slope) < 0.05:
        return "Scenario: Bearish caution (avoid fresh longs)."
    if 20 <= latest_rsi <= 40 and abs(macd_val) < 0.1 and abs(hist_slope) < 0.05:
        return "Scenario: Reversal likely / watch zone."
    if latest_rsi > 70:
        return "Scenario: Overbought – risk of correction."
    if latest_rsi < 30:
        return "Scenario: Oversold – possible bounce."

    return "Scenario: Neutral / range-bound – no strong edge."

# ---------- PVOI direction helper ----------
def get_pvo_directions(close_series, volume_series):
    price_dir = '↑' if close_series.iloc[-1] >= close_series.iloc[-2] else '↓'
    vol_dir = '↑' if volume_series.iloc[-1] >= volume_series.iloc[-2] else '↓'
    oi_dir = '↑' if volume_series.iloc[-1] >= volume_series.rolling(3).mean().iloc[-1] else '↓'
    return price_dir, vol_dir, oi_dir

# ---------- Full Nifty 50 Scanner ----------
def scan_all_nifty50(timeframe_key):
    config = TIMEFRAMES[timeframe_key]
    print(f"\n SCANNING ALL NIFTY 50 STOCKS ({config['name']})...")
    print("This may take 1-3 minutes...")
    
    bullish_stocks = []
    bearish_stocks = []
    neutral_stocks = []
    
    raw_data = yf.download(nifty50_symbols, period=config['period_scan'], 
                          interval=config['interval'], auto_adjust=True, group_by='ticker')
    
    for symbol in nifty50_symbols:
        try:
            if isinstance(raw_data.columns, pd.MultiIndex):
                if symbol in raw_data.columns.get_level_values(0):
                    close = raw_data[symbol]["Close"].dropna()
                else:
                    continue
            else:
                close = raw_data["Close"][symbol].dropna() if symbol in raw_data["Close"].columns else pd.Series()
            
            if len(close) < 30:
                neutral_stocks.append((symbol.replace('.NS', ''), "Not enough data"))
                continue
            
            rsi14_series = rsi(close, 14)
            macd_line, _, hist = macd(close, 12, 26, 9)
            
            rsi_val = rsi14_series.dropna().iloc[-1] if not rsi14_series.dropna().empty else np.nan
            macd_val = macd_line.dropna().iloc[-1] if not macd_line.dropna().empty else np.nan
            hist_clean = hist.dropna()
            hist_slope = (hist_clean.iloc[-1] - hist_clean.iloc[-2]) if len(hist_clean) >= 2 else np.nan
            
            scenario = classify_rsi_macd_scenario(rsi_val, macd_val, hist_slope)
            
            if "Bullish" in scenario:
                bullish_stocks.append((symbol.replace('.NS', ''), f"RSI:{rsi_val:.1f}, MACD:{macd_val:.3f}"))
            elif "Bearish" in scenario:
                bearish_stocks.append((symbol.replace('.NS', ''), f"RSI:{rsi_val:.1f}, MACD:{macd_val:.3f}"))
            else:
                neutral_stocks.append((symbol.replace('.NS', ''), f"RSI:{rsi_val:.1f}, MACD:{macd_val:.3f}"))
                
        except Exception as e:
            neutral_stocks.append((symbol.replace('.NS', ''), "Error"))
    
    # Display Results
    print("\n" + "="*80)
    print(f" NIFTY 50 {config['name']} SCAN RESULTS")
    print("="*80)
    
    print(f"\n BULLISH STOCKS ({len(bullish_stocks)})")
    print("-" * 50)
    for i, (stock, indicators) in enumerate(bullish_stocks[:10], 1):
        print(f"{i:2d}. {stock:<12} | {indicators}")
    if len(bullish_stocks) > 10:
        print(f"   ... and {len(bullish_stocks)-10} more")
    
    print(f"\n BEARISH STOCKS ({len(bearish_stocks)})")
    print("-" * 50)
    for i, (stock, indicators) in enumerate(bearish_stocks[:10], 1):
        print(f"{i:2d}. {stock:<12} | {indicators}")
    if len(bearish_stocks) > 10:
        print(f"   ... and {len(bearish_stocks)-10} more")
    
    print(f"\n NEUTRAL STOCKS ({len(neutral_stocks)})")
    print("-" * 50)
    for i, (stock, indicators) in enumerate(neutral_stocks[:10], 1):
        print(f"{i:2d}. {stock:<12} | {indicators}")
    if len(neutral_stocks) > 10:
        print(f"   ... and {len(neutral_stocks)-10} more")
    
    print(f"\n SUMMARY: Bullish={len(bullish_stocks)} | Bearish={len(bearish_stocks)} | Neutral={len(neutral_stocks)}")
    print("="*80)
    
    return bullish_stocks, bearish_stocks, neutral_stocks

# ---------- PVOI SCENARIOS (same for all timeframes) ----------
scenarios = [
    {'price': '↑', 'vol': '↑', 'oi': '↑', 'Direction': 'Bullish', 'signal': 'Strong Bullish (Long Build)', 'rsi_low': 55, 'rsi_high': 70, 'macd': 'Above 0, Hist ↑', 'action': 'STRONG BUY', 'win_low': 80, 'win_high': 90, 'risk': 'LOW'},
    {'price': '↑', 'vol': '↑', 'oi': '↓', 'Direction': 'Bullish', 'signal': 'Short Covering (Weak Rally)', 'rsi_low': 40, 'rsi_high': 55, 'macd': 'Above 0, Hist Flat', 'action': 'Buy Caution', 'win_low': 60, 'win_high': 70, 'risk': 'MEDIUM'},
    {'price': '↑', 'vol': '↓', 'oi': '↑', 'Direction': 'Bullish', 'signal': 'Quiet Accumulation', 'rsi_low': 60, 'rsi_high': 75, 'macd': 'Above 0, Stable', 'action': 'BUY Setup Valid', 'win_low': 75, 'win_high': 85, 'risk': 'MED-HIGH'},
    {'price': '↑', 'vol': '↓', 'oi': '↓', 'Direction': 'Bullish', 'signal': 'Profit-Taking Reversal', 'rsi_low': 45, 'rsi_high': 60, 'macd': 'Above 0, Hist ↓', 'action': 'EXIT/SKIP', 'win_low': 30, 'win_high': 40, 'risk': 'HIGH'},
    {'price': '↓', 'vol': '↑', 'oi': '↑', 'Direction': 'Bearish', 'signal': 'Strong Bearish (Short Build)', 'rsi_low': 20, 'rsi_high': 40, 'macd': 'Below 0, Hist ↓', 'action': 'STRONG SELL', 'win_low': 70, 'win_high': 80, 'risk': 'LOW'},
    {'price': '↓', 'vol': '↑', 'oi': '↓', 'Direction': 'Bearish', 'signal': 'Liquidation (Panic)', 'rsi_low': 20, 'rsi_high': 35, 'macd': 'Below 0, Hist ↑', 'action': 'Exit Shorts', 'win_low': 50, 'win_high': 60, 'risk': 'HIGH'},
    {'price': '↓', 'vol': '↓', 'oi': '↑', 'Direction': 'Bearish', 'signal': 'Bearish Caution', 'rsi_low': 30, 'rsi_high': 50, 'macd': 'Below 0, Stable', 'action': 'AVOID', 'win_low': 30, 'win_high': 40, 'risk': 'MEDIUM'},
    {'price': '↓', 'vol': '↓', 'oi': '↓', 'Direction': 'Bearish', 'signal': 'Reversal Likely', 'rsi_low': 20, 'rsi_high': 40, 'macd': 'Crossing 0', 'action': 'WATCH', 'win_low': 40, 'win_high': 50, 'risk': 'MEDIUM'}
]

df_scenarios = pd.DataFrame(scenarios)
df_scenarios["win_avg"] = (df_scenarios["win_low"] + df_scenarios["win_high"]) / 2
risk_order = {"LOW": 0, "MEDIUM": 1, "MED-HIGH": 2, "HIGH": 3}
df_scenarios["risk_rank"] = df_scenarios["risk"].map(risk_order)

def macd_matches(macd_line, hist_slope, macd_condition):
    if 'Above 0' in macd_condition and macd_line <= 0: return False
    if 'Below 0' in macd_condition and macd_line >= 0: return False
    if 'Crossing 0' in macd_condition and abs(macd_line) > 0.1: return False
    if 'Hist ↑' in macd_condition and hist_slope <= 0: return False
    if 'Hist ↓' in macd_condition and hist_slope >= 0: return False
    if 'Hist Flat' in macd_condition and abs(hist_slope) > 0.05: return False
    if 'Stable' in macd_condition and abs(hist_slope) > 0.1: return False
    return True

def classify_pvoi_rsi_macd(price_dir, vol_dir, oi_dir, rsi_val, macd_line, hist_slope):
    candidates = df_scenarios[(df_scenarios['price'] == price_dir) &
                             (df_scenarios['vol'] == vol_dir) &
                             (df_scenarios['oi'] == oi_dir)]
    for _, row in candidates.iterrows():
        if row['rsi_low'] <= rsi_val <= row['rsi_high'] and macd_matches(macd_line, hist_slope, row['macd']):
            win_rate_avg = (row['win_low'] + row['win_high']) / 2
            return {
                "Direction": row["Direction"], "Signal": row["signal"],
                "Action": row["action"], "Win Rate (%)": f"{win_rate_avg:.1f}",
                "Risk Level": row["risk"]
            }
    return None

# ---------- SINGLE STOCK ANALYSIS ----------
def single_stock_analysis(timeframe_key):
    config = TIMEFRAMES[timeframe_key]
    symbol = pick_single_stock()
    print(f"\nYou selected: {symbol}")
    print(f"Downloading {config['name'].lower()} data...")
    
    data = yf.download(symbol, period=config['period_single'], interval=config['interval'], auto_adjust=True)
    if data.empty:
        print("No data found.")
        return

    close = data["Close"].squeeze()
    volume = data["Volume"].squeeze()

    sma_short = close.rolling(window=config['sma_short']).mean()
    sma_long = close.rolling(window=config['sma_long']).mean()

    rsi7 = rsi(close, 7)
    rsi14 = rsi(close, 14)
    rsi28 = rsi(close, 28)
    macd_line, signal_line, hist = macd(close, 12, 26, 9)

    fig, (ax_price, ax_vol, ax_rsi, ax_macd) = plt.subplots(
        nrows=4, ncols=1, sharex=True, figsize=(14, 12),
        gridspec_kw={"height_ratios": [3, 1, 1, 1]}
    )

    ax_price.plot(close.index, close.values, label=f"{config['name']} Close", color="black", linewidth=2)
    ax_price.plot(sma_short.index, sma_short.values, label=f"{config['sma_short']}{timeframe_key} SMA", color="blue", linewidth=1.5)
    ax_price.plot(sma_long.index, sma_long.values, label=f"{config['sma_long']}{timeframe_key} SMA", color="orange", linewidth=1.5)
    ax_price.set_ylabel("Price (INR)")
    ax_price.set_title(f"{symbol} {config['name']} Analysis: Price, SMA, RSI & MACD")
    ax_price.legend()
    ax_price.grid(alpha=0.3)

    ax_vol.bar(volume.index, volume.values, color="grey", width=0.8, alpha=0.7)
    ax_vol.set_ylabel(f"{config['name']} Volume")
    ax_vol.grid(alpha=0.3)

    ax_rsi.plot(rsi7.index, rsi7.values, label="RSI 7", color="green")
    ax_rsi.plot(rsi14.index, rsi14.values, label="RSI 14", color="blue")
    ax_rsi.plot(rsi28.index, rsi28.values, label="RSI 28", color="orange")
    ax_rsi.axhline(70, color="red", linestyle="--", linewidth=1)
    ax_rsi.axhline(30, color="green", linestyle="--", linewidth=1)
    ax_rsi.set_ylabel(f"{config['name']} RSI")
    ax_rsi.legend(loc="upper left")
    ax_rsi.grid(alpha=0.3)

    ax_macd.plot(macd_line.index, macd_line.values, label="MACD (12,26)", color="purple")
    ax_macd.plot(signal_line.index, signal_line.values, label="Signal (9)", color="orange")
    ax_macd.bar(hist.index, hist.values, label="Histogram", color="grey", alpha=0.6)
    ax_macd.axhline(0, color="black", linewidth=1)
    ax_macd.set_ylabel(f"{config['name']} MACD")
    ax_macd.set_xlabel("Date")
    ax_macd.legend(loc="upper left")
    ax_macd.grid(alpha=0.3)

    plt.tight_layout()
    plt.show()

    # Latest values
    latest_rsi = rsi14.dropna().iloc[-1] if not rsi14.dropna().empty else np.nan
    hist_clean = hist.dropna()
    hist_slope = (hist_clean.iloc[-1] - hist_clean.iloc[-2]) if len(hist_clean) >= 2 else np.nan
    latest_macd = macd_line.dropna().iloc[-1] if not macd_line.dropna().empty else np.nan

    scenario_text = classify_rsi_macd_scenario(latest_rsi, latest_macd, hist_slope)
    price_dir, vol_dir, oi_dir = get_pvo_directions(close, volume)
    pvoi_result = classify_pvoi_rsi_macd(price_dir, vol_dir, oi_dir, latest_rsi, latest_macd, hist_slope)

    print(f"\n{config['name']} RSI14: {latest_rsi:.2f} | MACD: {latest_macd:.4f} | HistΔ: {hist_slope:.4f}")
    print(scenario_text)
    print(f"\n=== {config['name']} PVOI RESULT ===")
    print(f"Price: {price_dir} | Vol: {vol_dir} | OI: {oi_dir}")
    if pvoi_result:
        print(f"Signal: {pvoi_result['Direction']} ({pvoi_result['Signal']})")
        print(f"Action: {pvoi_result['Action']} | Win: {pvoi_result['Win Rate (%)']}% | Risk: {pvoi_result['Risk Level']}")
    else:
        print("No matching PVOI scenario.")

# ---------- MULTIPLE STOCK COMPARISON ----------
def multiple_stock_comparison(timeframe_key):
    config = TIMEFRAMES[timeframe_key]
    print(f"\nMULTIPLE STOCK {config['name']} COMPARISON ({config['period_compare']})")
    print("Enter stock numbers (space-separated, max 5).")
    
    for i, s in enumerate(nifty50_symbols, start=1):
        print(f"{i:2d}. {s.replace('.NS','')}")
    
    inp = input("Your choices: ").strip().split()
    idxs = [int(x)-1 for x in inp if x.isdigit() and 1 <= int(x) <= len(nifty50_symbols)]
    idxs = list(dict.fromkeys(idxs))[:5]
    
    if not idxs:
        print("No valid choices.")
        return
        
    syms = [nifty50_symbols[i] for i in idxs]
    print(f"Comparing {config['name'].lower()}: {', '.join([s.replace('.NS','') for s in syms])}")

    raw = yf.download(syms, period=config['period_compare'], interval=config['interval'], 
                     auto_adjust=True)[["Close"]]
    
    if raw.empty or isinstance(raw.columns, pd.MultiIndex):
        close_panel = raw["Close"]
    else:
        close_panel = raw

    norm = (close_panel / close_panel.iloc[0] - 1) * 100.0

    fig, (ax_perf, ax_rsi, ax_macd) = plt.subplots(3, 1, sharex=True, figsize=(14, 12),
                                                  gridspec_kw={"height_ratios": [2, 1, 1]})

    for s in syms:
        ax_perf.plot(norm.index, norm[s].values, label=s.replace(".NS", ""), linewidth=2)
    ax_perf.set_title(f"{config['period_compare']} {config['name']} % Performance")
    ax_perf.set_ylabel("% Change")
    ax_perf.legend()
    ax_perf.grid(alpha=0.3)

    # Simplified RSI/MACD overlay (latest values only for print)
    latest_rsi, latest_macd, hist_slopes = {}, {}, {}
    for s in syms:
        close = close_panel[s].dropna()
        if len(close) < 30: continue
        
        rsi14_series = rsi(close, 14)
        macd_line, _, hist = macd(close, 12, 26, 9)
        
        if not rsi14_series.dropna().empty:
            latest_rsi[s] = rsi14_series.dropna().iloc[-1]
        if not macd_line.dropna().empty:
            latest_macd[s] = macd_line.dropna().iloc[-1]
        hist_clean = hist.dropna()
        if len(hist_clean) >= 2:
            hist_slopes[s] = hist_clean.iloc[-1] - hist_clean.iloc[-2]

    print(f"\n{config['name']} Scenarios:")
    for sym in syms:
        r, m, h = latest_rsi.get(sym, np.nan), latest_macd.get(sym, np.nan), hist_slopes.get(sym, np.nan)
        scenario = classify_rsi_macd_scenario(r, m, h)
        print(f"{sym.replace('.NS','')}: RSI={r:.1f}, MACD={m:.4f}, HistΔ={h:.4f} -> {scenario}")

    plt.tight_layout()
    plt.show()

# ---------- UTILITY FUNCTIONS ----------
def pick_single_stock():
    print("\nNifty 50 Stocks:")
    for i, s in enumerate(nifty50_symbols, start=1):
        print(f"{i:2d}. {s.replace('.NS','')}")
    while True:
        inp = input("Enter stock number: ").strip()
        if inp.isdigit() and 1 <= int(inp) <= len(nifty50_symbols):
            return nifty50_symbols[int(inp)-1]
        print("Enter valid number (1-50).")

def print_scenario_rankings(timeframe_name):
    bulls = df_scenarios[df_scenarios["Direction"] == "Bullish"].sort_values(["win_avg", "risk_rank"], ascending=[False, True])
    bears = df_scenarios[df_scenarios["Direction"] == "Bearish"].sort_values(["win_avg", "risk_rank"], ascending=[False, True])
    
    print(f"\n=== BULLISH Scenarios ({timeframe_name}) ===")
    print(bulls[["signal", "action", "win_avg", "risk"]].round(1).to_string(index=False))
    print(f"\n=== BEARISH Scenarios ({timeframe_name}) ===")
    print(bears[["signal", "action", "win_avg", "risk"]].round(1).to_string(index=False))

# ---------- MAIN MENU ----------
def print_menu():
    print("\n" + "="*80)
    print("         NIFTY 50 MULTI-TIMEFRAME ANALYZER v3.0 🔥")
    print("="*80)
    print("TIMEFRAME SELECTION:")
    print("1.  DAILY Analysis (Intraday/Swing)")
    print("2.  WEEKLY Analysis (Swing/Positional)")
    print("3.  MONTHLY Analysis (Long-term/Investment)")
    print("\nDAILY ANALYZER:")
    print("11. Scan ALL Nifty 50 (Daily)")
    print("12. Single Stock Daily Analysis")
    print("13. Multiple Stock Daily Comparison")
    print("\nWEEKLY ANALYZER:")
    print("21. Scan ALL Nifty 50 (Weekly)")
    print("22. Single Stock Weekly Analysis")
    print("23. Multiple Stock Weekly Comparison")
    print("\nMONTHLY ANALYZER:")
    print("31. Scan ALL Nifty 50 (Monthly)")
    print("32. Single Stock Monthly Analysis")
    print("33. Multiple Stock Monthly Comparison")
    print("\nSCENARIO ANALYSIS:")
    print("41. Bullish Scenarios Ranking")
    print("42. Bearish Scenarios Ranking")
    print("0.  Exit")
    print("="*80)

# ---------- MAIN LOOP ----------
if __name__ == "__main__":
    while True:
        print_menu()
        ch = input("Enter choice: ").strip()
        
        if ch == "0":
            print("Goodbye!")
            break
        elif ch == "1":
            print_scenario_rankings("ALL TIMEFRAMES")
        elif ch == "11":
            scan_all_nifty50('daily')
        elif ch == "12":
            single_stock_analysis('daily')
        elif ch == "13":
            multiple_stock_comparison('daily')
        elif ch == "21":
            scan_all_nifty50('weekly')
        elif ch == "22":
            single_stock_analysis('weekly')
        elif ch == "23":
            multiple_stock_comparison('weekly')
        elif ch == "31":
            scan_all_nifty50('monthly')
        elif ch == "32":
            single_stock_analysis('monthly')
        elif ch == "33":
            multiple_stock_comparison('monthly')
        elif ch == "41":
            print_scenario_rankings("Bullish")
        elif ch == "42":
            print_scenario_rankings("Bearish")
        else:
            print(" Invalid choice. Try again.")
