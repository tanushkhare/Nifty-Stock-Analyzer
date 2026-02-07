import yfinance as yf
import pandas as pd
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
def macd(series: pd.Series,
         fast: int = 12,
         slow: int = 26,
         signal: int = 9):
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    hist = macd_line - signal_line
    return macd_line, signal_line, hist


# ---------- RSI+MACD text classifier ----------
def classify_rsi_macd_scenario(latest_rsi: float,
                               macd_val: float,
                               hist_slope: float) -> str:
    if pd.isna(latest_rsi) or pd.isna(macd_val) or pd.isna(hist_slope):
        return "Scenario: Not enough data."

    if 55 <= latest_rsi <= 70 and macd_val > 0 and hist_slope > 0:
        return "Scenario: Strong Bullish (long build – strong buy zone, but watch for overbought)."

    if 40 <= latest_rsi < 55 and macd_val > 0 and abs(hist_slope) < 0.05:
        return "Scenario: Short covering / weak rally (buy with caution)."

    if 60 <= latest_rsi <= 75 and macd_val > 0 and abs(hist_slope) < 0.1:
        return "Scenario: Quiet accumulation (buy setup valid, medium–high confidence)."

    if 45 <= latest_rsi <= 60 and macd_val > 0 and hist_slope < 0:
        return "Scenario: Profit‑taking or early reversal (consider partial exit/skip new buys)."

    if 20 <= latest_rsi <= 40 and macd_val < 0 and hist_slope < 0:
        return "Scenario: Strong Bearish (short build – strong sell bias)."

    if 20 <= latest_rsi <= 35 and macd_val < 0 and hist_slope > 0:
        return "Scenario: Liquidation / panic washout – shorts may start covering."

    if 30 <= latest_rsi <= 50 and macd_val < 0 and abs(hist_slope) < 0.05:
        return "Scenario: Bearish caution (avoid fresh longs; trend weak)."

    if 20 <= latest_rsi <= 40 and abs(macd_val) < 0.1 and abs(hist_slope) < 0.05:
        return "Scenario: Reversal likely / watch zone (momentum turning)."

    if latest_rsi > 70:
        return "Scenario: Overbought – upside limited, risk of correction."
    if latest_rsi < 30:
        return "Scenario: Oversold – high volatility, possible bounce."

    return "Scenario: Neutral / range‑bound – no strong directional edge."


# ---------- PVOI SCENARIOS + FORMULA ----------
scenarios = [
    {'price': '↑', 'vol': '↑', 'oi': '↑', 'Direction': 'Bullish',
     'signal': 'Strong Bullish (Long Build)', 'rsi_low': 55, 'rsi_high': 70,
     'macd': 'Above 0, Hist ↑', 'action': 'STRONG BUY',
     'win_low': 80, 'win_high': 90, 'risk': 'LOW'},

    {'price': '↑', 'vol': '↑', 'oi': '↓', 'Direction': 'Bullish',
     'signal': 'Short Covering (Weak Rally)', 'rsi_low': 40, 'rsi_high': 55,
     'macd': 'Above 0, Hist Flat', 'action': 'Buy Caution',
     'win_low': 60, 'win_high': 70, 'risk': 'MEDIUM'},

    {'price': '↑', 'vol': '↓', 'oi': '↑', 'Direction': 'Bullish',
     'signal': 'Quiet Accumulation', 'rsi_low': 60, 'rsi_high': 75,
     'macd': 'Above 0, Stable', 'action': 'BUY Setup Valid',
     'win_low': 75, 'win_high': 85, 'risk': 'MED-HIGH'},

    {'price': '↑', 'vol': '↓', 'oi': '↓', 'Direction': 'Bullish',
     'signal': 'Profit-Taking Reversal', 'rsi_low': 45, 'rsi_high': 60,
     'macd': 'Above 0, Hist ↓', 'action': 'EXIT/SKIP',
     'win_low': 30, 'win_high': 40, 'risk': 'HIGH'},

    {'price': '↓', 'vol': '↑', 'oi': '↑', 'Direction': 'Bearish',
     'signal': 'Strong Bearish (Short Build)', 'rsi_low': 20, 'rsi_high': 40,
     'macd': 'Below 0, Hist ↓', 'action': 'STRONG SELL',
     'win_low': 70, 'win_high': 80, 'risk': 'LOW'},

    {'price': '↓', 'vol': '↑', 'oi': '↓', 'Direction': 'Bearish',
     'signal': 'Liquidation (Panic)', 'rsi_low': 20, 'rsi_high': 35,
     'macd': 'Below 0, Hist ↑', 'action': 'Exit Shorts',
     'win_low': 50, 'win_high': 60, 'risk': 'HIGH'},

    {'price': '↓', 'vol': '↓', 'oi': '↑', 'Direction': 'Bearish',
     'signal': 'Bearish Caution', 'rsi_low': 30, 'rsi_high': 50,
     'macd': 'Below 0, Stable', 'action': 'AVOID',
     'win_low': 30, 'win_high': 40, 'risk': 'MEDIUM'},

    {'price': '↓', 'vol': '↓', 'oi': '↓', 'Direction': 'Bearish',
     'signal': 'Reversal Likely', 'rsi_low': 20, 'rsi_high': 40,
     'macd': 'Crossing 0', 'action': 'WATCH',
     'win_low': 40, 'win_high': 50, 'risk': 'MEDIUM'}
]

df = pd.DataFrame(scenarios)
df["win_avg"] = (df["win_low"] + df["win_high"]) / 2
risk_order = {"LOW": 0, "MEDIUM": 1, "MED-HIGH": 2, "HIGH": 3}
df["risk_rank"] = df["risk"].map(risk_order)


def macd_matches(macd_line, hist_slope, macd_condition):
    if 'Above 0' in macd_condition and macd_line <= 0:
        return False
    if 'Below 0' in macd_condition and macd_line >= 0:
        return False
    if 'Crossing 0' in macd_condition and abs(macd_line) > 0.1:
        return False

    if 'Hist ↑' in macd_condition and hist_slope <= 0:
        return False
    if 'Hist ↓' in macd_condition and hist_slope >= 0:
        return False
    if 'Hist Flat' in macd_condition and abs(hist_slope) > 0.05:
        return False
    if 'Stable' in macd_condition and abs(hist_slope) > 0.1:
        return False
    return True


def classify_pvoi_rsi_macd(price_dir, vol_dir, oi_dir, rsi_val, macd_line, hist_slope):
    candidates = df[(df['price'] == price_dir) &
                    (df['vol'] == vol_dir) &
                    (df['oi'] == oi_dir)]
    for _, row in candidates.iterrows():
        if row['rsi_low'] <= rsi_val <= row['rsi_high'] and macd_matches(macd_line, hist_slope, row['macd']):
            win_rate_avg = (row['win_low'] + row['win_high']) / 2
            return {
                "Direction": row["Direction"],
                "Signal": row["signal"],
                "Action": row["action"],
                "Win Rate (%)": f"{win_rate_avg:.1f}",
                "Risk Level": row["risk"]
            }
    return None


# ---------- SCENARIO RANKING PRINTER ----------
def print_scenario_ranking():
    ranked = df.sort_values(["win_avg", "risk_rank"], ascending=[False, True])
    cols = ["Direction", "signal", "action", "win_low", "win_high", "win_avg", "risk"]
    print("\n=== PVOI + RSI + MACD Scenario Ranking (by win-rate) ===")
    print(ranked[cols].to_string(index=False, formatters={
        "win_low":  lambda x: f"{x:.0f}",
        "win_high": lambda x: f"{x:.0f}",
        "win_avg":  lambda x: f"{x:.1f}"
    }))


# simple direction helper (price, volume; OI proxy from volume)
def get_pvo_directions(close_series, volume_series):
    price_dir = '↑' if close_series.iloc[-1] >= close_series.iloc[-2] else '↓'
    vol_dir = '↑' if volume_series.iloc[-1] >= volume_series.iloc[-2] else '↓'
    # proxy OI: compare today volume vs 3‑day average
    oi_dir = '↑' if volume_series.iloc[-1] >= volume_series.rolling(3).mean().iloc[-1] else '↓'
    return price_dir, vol_dir, oi_dir


# ---------- menu ----------
def print_menu():
    print("\n" + "="*60)
    print("          NIFTY 50 ANALYZER")
    print("="*60)
    print("1. Single Stock Analysis (price + SMA + volume + RSI 7/14/28 + MACD + scenario + PVOI win-rate)")
    print("2. Multiple Stock Comparison (3M % performance + RSI(14) + MACD + scenario)")
    print("3. All Stocks - Today High")
    print("4. All Stocks - Today Low")
    print("5. Best & Worst Performer (1D % change)")
    print("6. Scenario Ranking (PVOI + RSI + MACD)")
    print("0. Exit")
    print("-"*60)


def pick_single_stock():
    print("\nNifty 50 Stocks:")
    for i, s in enumerate(nifty50_symbols, start=1):
        print(f"{i:2d}. {s}")
    while True:
        inp = input("Enter stock number: ").strip()
        if not inp or not inp.isdigit():
            print("Enter a valid number.")
            continue
        num = int(inp)
        if 1 <= num <= len(nifty50_symbols):
            return nifty50_symbols[num-1]
        print(f"Enter between 1 and {len(nifty50_symbols)}.")


# ---------- SINGLE STOCK ANALYSIS WITH PVOI ----------
def single_stock_analysis():
    symbol = pick_single_stock()
    print(f"\nYou selected: {symbol}")
    print("Downloading data...")
    data = yf.download(symbol, period="6mo", interval="1d", auto_adjust=True)
    if data.empty:
        print("No data found.")
        return

    close = data["Close"].squeeze()
    volume = data["Volume"].squeeze()

    short_window = 20
    long_window = 50
    sma20 = close.rolling(window=short_window).mean()
    sma50 = close.rolling(window=long_window).mean()

    rsi7 = rsi(close, 7)
    rsi14 = rsi(close, 14)
    rsi28 = rsi(close, 28)

    macd_line, signal_line, hist = macd(close, 12, 26, 9)

    fig, (ax_price, ax_vol, ax_rsi_ax, ax_macd) = plt.subplots(
        nrows=4, ncols=1, sharex=True, figsize=(12, 12),
        gridspec_kw={"height_ratios": [3, 1, 1, 1]}
    )

    ax_price.plot(close.index, close.values, label="Close", color="black", linewidth=1.5)
    ax_price.plot(sma20.index, sma20.values, label="20-day SMA", color="blue", linewidth=1.2)
    ax_price.plot(sma50.index, sma50.values, label="50-day SMA", color="orange", linewidth=1.2)
    ax_price.set_ylabel("Price (INR)")
    ax_price.set_title(f"{symbol} Price, SMA, RSI & MACD (6M)")
    ax_price.legend()
    ax_price.grid(alpha=0.3)

    ax_vol.bar(volume.index, volume.values, color="grey", width=1.0, linewidth=0.0)
    ax_vol.set_ylabel("Volume")
    ax_vol.grid(alpha=0.3)

    ax_rsi_ax.plot(rsi7.index, rsi7.values, label="RSI 7", color="green")
    ax_rsi_ax.plot(rsi14.index, rsi14.values, label="RSI 14", color="blue")
    ax_rsi_ax.plot(rsi28.index, rsi28.values, label="RSI 28", color="orange")
    ax_rsi_ax.axhline(70, color="red", linestyle="--", linewidth=0.8)
    ax_rsi_ax.axhline(30, color="green", linestyle="--", linewidth=0.8)
    ax_rsi_ax.set_ylabel("RSI")
    ax_rsi_ax.legend(loc="upper left")
    ax_rsi_ax.grid(alpha=0.3)

    ax_macd.plot(macd_line.index, macd_line.values, label="MACD (12,26)", color="purple")
    ax_macd.plot(signal_line.index, signal_line.values, label="Signal (9)", color="orange")
    ax_macd.bar(hist.index, hist.values, label="Histogram", color="grey", alpha=0.5)
    ax_macd.axhline(0, color="black", linewidth=0.8)
    ax_macd.set_ylabel("MACD")
    ax_macd.set_xlabel("Date")
    ax_macd.legend(loc="upper left")
    ax_macd.grid(alpha=0.3)

    plt.tight_layout()
    plt.show()

    # latest indicator values
    rsi14_clean = rsi14.dropna()
    latest_rsi = rsi14_clean.iloc[-1] if not rsi14_clean.empty else float("nan")

    hist_clean = hist.dropna()
    if len(hist_clean) >= 2:
        last_hist = hist_clean.iloc[-1]
        prev_hist = hist_clean.iloc[-2]
        hist_slope = last_hist - prev_hist
    else:
        hist_slope = float("nan")

    macd_clean = macd_line.dropna()
    latest_macd = macd_clean.iloc[-1] if not macd_clean.empty else float("nan")

    scenario_text = classify_rsi_macd_scenario(latest_rsi, latest_macd, hist_slope)

    # PVOI directions + formula evaluation
    price_dir, vol_dir, oi_dir = get_pvo_directions(close, volume)
    pvoi_result = classify_pvoi_rsi_macd(price_dir, vol_dir, oi_dir,
                                         latest_rsi, latest_macd, hist_slope)

    print(f"RSI14: {latest_rsi:.2f} | MACD: {latest_macd:.4f} | Hist change: {hist_slope:.4f}")
    print(scenario_text)

    print("\n=== PVOI FORMULA RESULT (Primary) ===")
    print(f"Price Dir: {price_dir} | Volume Dir: {vol_dir} | OI Dir (proxy): {oi_dir}")
    if pvoi_result:
        print(f"Market Bias : {pvoi_result['Direction']}  ({pvoi_result['Signal']})")
        print(f"Trade Action: {pvoi_result['Action']}")
        print(f"Win Rate    : {pvoi_result['Win Rate (%)']} %")
        print(f"Risk Level  : {pvoi_result['Risk Level']}")
    else:
        print("No matching scenario found for current P+V+OI + RSI + MACD.")


# ---------- MULTIPLE STOCK COMPARISON ----------
def multiple_stock_comparison():
    print("\nMULTIPLE STOCK COMPARISON (3 Months)")
    print("Enter stock numbers (space-separated, max 5).")
    for i, s in enumerate(nifty50_symbols, start=1):
        print(f"{i:2d}. {s}")
    inp = input("Your choices: ").strip().split()
    idxs = []
    for x in inp:
        if x.isdigit():
            v = int(x)
            if 1 <= v <= len(nifty50_symbols):
                idxs.append(v-1)
    idxs = list(dict.fromkeys(idxs))[:5]
    if not idxs:
        print("No valid choices.")
        return
    syms = [nifty50_symbols[i] for i in idxs]
    print("Comparing:", ", ".join(syms))

    raw = yf.download(syms, period="3mo", interval="1d", auto_adjust=True)[["Close"]]
    if raw.empty:
        print("No data downloaded.")
        return

    if isinstance(raw.columns, pd.MultiIndex):
        close_panel = raw["Close"]
    else:
        if len(syms) == 1:
            close_panel = pd.DataFrame({syms[0]: raw["Close"]})
        else:
            close_panel = raw

    norm = (close_panel / close_panel.iloc[0] - 1) * 100.0

    fig, (ax_perf, ax_rsi_ax, ax_macd_ax) = plt.subplots(
        nrows=3, ncols=1, sharex=True, figsize=(12, 10),
        gridspec_kw={"height_ratios": [2, 1, 1]}
    )

    for s in syms:
        ax_perf.plot(norm.index, norm[s].values, label=s.replace(".NS", ""), linewidth=1.5)
    ax_perf.set_title("3‑Month % Performance")
    ax_perf.set_ylabel("% Change from Start")
    ax_perf.grid(alpha=0.3)
    ax_perf.legend()

    latest_rsi_values = {}
    latest_macd_vals = {}
    hist_slopes = {}

    for s in syms:
        close = close_panel[s].dropna()
        rsi14_series = rsi(close, 14)
        ax_rsi_ax.plot(rsi14_series.index, rsi14_series.values,
                       label=f"{s.replace('.NS','')} RSI14", linewidth=1.0)
        if not rsi14_series.dropna().empty:
            latest_rsi_values[s] = rsi14_series.dropna().iloc[-1]

    ax_rsi_ax.axhline(70, color="red", linestyle="--", linewidth=0.8)
    ax_rsi_ax.axhline(30, color="green", linestyle="--", linewidth=0.8)
    ax_rsi_ax.set_ylabel("RSI 14")
    ax_rsi_ax.grid(alpha=0.3)
    ax_rsi_ax.legend(loc="upper left", fontsize=8)

    for s in syms:
        close = close_panel[s].dropna()
        macd_line, signal_line, hist = macd(close, 12, 26, 9)
        ax_macd_ax.plot(macd_line.index, macd_line.values,
                        label=f"{s.replace('.NS','')} MACD12", linewidth=1.0)
        if not macd_line.dropna().empty:
            latest_macd_vals[s] = macd_line.dropna().iloc[-1]
        hist_clean = hist.dropna()
        if len(hist_clean) >= 2:
            last_hist = hist_clean.iloc[-1]
            prev_hist = hist_clean.iloc[-2]
            hist_slopes[s] = last_hist - prev_hist

    ax_macd_ax.axhline(0, color="black", linewidth=0.8)
    ax_macd_ax.set_ylabel("MACD 12/26")
    ax_macd_ax.set_xlabel("Date")
    ax_macd_ax.grid(alpha=0.3)
    ax_macd_ax.legend(loc="upper left", fontsize=8)

    plt.tight_layout()
    plt.show()

    print("\nRSI + MACD scenario for selected stocks:")
    for sym in syms:
        r = latest_rsi_values.get(sym, float("nan"))
        m = latest_macd_vals.get(sym, float("nan"))
        h = hist_slopes.get(sym, float("nan"))
        scenario = classify_rsi_macd_scenario(r, m, h)
        if pd.isna(r) or pd.isna(m) or pd.isna(h):
            print(f"{sym}: Not enough data for scenario.")
        else:
            print(f"{sym}: RSI14={r:.1f}, MACD={m:.4f}, HistΔ={h:.4f} -> {scenario}")


# ---------- remaining helpers ----------
def _one_day_returns():
    data = yf.download(nifty50_symbols, period="2d", group_by="ticker", auto_adjust=True)
    changes = {}
    for sym in nifty50_symbols:
        try:
            prices = data["Close"][sym].dropna()
            if len(prices) >= 2:
                c, p = prices.iloc[-1], prices.iloc[-2]
                changes[sym] = (c - p) / p * 100.0
        except Exception:
            continue
    return changes


def all_day_high():
    print("\nAll stocks - Today High:")
    data = yf.download(nifty50_symbols, period="1d", group_by="ticker", auto_adjust=False)
    for sym in nifty50_symbols:
        try:
            high_val = data["High"][sym].dropna().iloc[-1]
            print(f"{sym}: High = {high_val:.2f}")
        except Exception:
            pass


def all_day_low():
    print("\nAll stocks - Today Low:")
    data = yf.download(nifty50_symbols, period="1d", group_by="ticker", auto_adjust=False)
    for sym in nifty50_symbols:
        try:
            low_val = data["Low"][sym].dropna().iloc[-1]
            print(f"{sym}: Low = {low_val:.2f}")
        except Exception:
            pass


def best_performer():
    print("\nBest & Worst Performer (1‑Day % Change)")
    changes = _one_day_returns()
    if not changes:
        print("No data.")
        return
    ser = pd.Series(changes)
    best = ser.sort_values(ascending=False).head(5)
    worst = ser.sort_values(ascending=True).head(5)

    print("\nTop 5 gainers:")
    for s, v in best.items():
        print(f"{s}: {v:+.2f}%")

    print("\nTop 5 losers:")
    for s, v in worst.items():
        print(f"{s}: {v:+.2f}%")


# ---------- MAIN LOOP ----------
while True:
    print_menu()
    ch = input("Enter your choice (0‑6): ").strip()
    if ch == "0":
        print("Goodbye!")
        break
    elif ch == "1":
        single_stock_analysis()
    elif ch == "2":
        multiple_stock_comparison()
    elif ch == "3":
        all_day_high()
    elif ch == "4":
        all_day_low()
    elif ch == "5":
        best_performer()
    elif ch == "6":
        print_scenario_ranking()
    else:
        print("Invalid choice. Try again.")
