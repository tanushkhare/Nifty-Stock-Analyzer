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

# ---------- menu etc. ----------

def print_menu():
    print("\n" + "="*60)
    print("          NIFTY 50 ANALYZER")
    print("="*60)
    print("1. Single Stock Analysis (price + SMA + volume + RSI 7/14/28)")
    print("2. Multiple Stock Comparison (3M % performance + RSI(14) + RSI trend)")
    print("3. All Stocks - Today High")
    print("4. All Stocks - Today Low")
    print("5. Best & Worst Performer (1D % change)")
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

# ---------- SINGLE STOCK WITH RSI(7/14/28) ----------

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

    fig, (ax_price, ax_vol, ax_rsi) = plt.subplots(
        nrows=3, ncols=1, sharex=True, figsize=(12, 10),
        gridspec_kw={"height_ratios": [3, 1, 1]}
    )

    ax_price.plot(close.index, close.values, label="Close", color="black", linewidth=1.5)
    ax_price.plot(close.index, sma20.values, label="20-day SMA", color="blue", linewidth=1.2)
    ax_price.plot(close.index, sma50.values, label="50-day SMA", color="orange", linewidth=1.2)
    ax_price.set_ylabel("Price (INR)")
    ax_price.set_title(f"{symbol} Price, SMA & RSI (6M)")
    ax_price.legend()
    ax_price.grid(alpha=0.3)

    ax_vol.bar(volume.index, volume.values, color="grey", width=1.0, linewidth=0.0)
    ax_vol.set_ylabel("Volume")
    ax_vol.grid(alpha=0.3)

    ax_rsi.plot(rsi7.index, rsi7.values, label="RSI 7", color="green")
    ax_rsi.plot(rsi14.index, rsi14.values, label="RSI 14", color="blue")
    ax_rsi.plot(rsi28.index, rsi28.values, label="RSI 28", color="orange")
    ax_rsi.axhline(70, color="red", linestyle="--", linewidth=0.8)
    ax_rsi.axhline(30, color="green", linestyle="--", linewidth=0.8)
    ax_rsi.set_ylabel("RSI")
    ax_rsi.set_xlabel("Date")
    ax_rsi.legend(loc="upper left")
    ax_rsi.grid(alpha=0.3)

    plt.tight_layout()
    plt.show()

    if pd.notna(sma20.iloc[-1]) and pd.notna(sma50.iloc[-1]):
        if sma20.iloc[-1] > sma50.iloc[-1]:
            print("Bullish trend: Consider buying (do more research!).")
        else:
            print("Bearish trend: Not a good time to buy.")
    else:
        print("Not enough data for moving average analysis.")

# ---------- MULTIPLE STOCKS WITH RSI(14) + RSI-BASED TREND ----------

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

    fig, (ax_perf, ax_rsi_ax) = plt.subplots(
        nrows=2, ncols=1, sharex=True, figsize=(12, 8),
        gridspec_kw={"height_ratios": [2, 1]}
    )

    # Performance lines
    for s in syms:
        ax_perf.plot(norm.index, norm[s].values, label=s.replace(".NS", ""), linewidth=1.5)
    ax_perf.set_title("3‑Month % Performance")
    ax_perf.set_ylabel("% Change from Start")
    ax_perf.grid(alpha=0.3)
    ax_perf.legend()

    # RSI(14) lines
    latest_rsi_values = {}
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
    ax_rsi_ax.set_xlabel("Date")
    ax_rsi_ax.grid(alpha=0.3)
    ax_rsi_ax.legend(loc="upper left", fontsize=8)

    plt.tight_layout()
    plt.show()

    # Trend summary based on latest RSI(14)
    print("\nRSI-based trend for selected stocks (using RSI 14):")
    for sym in syms:
        r = latest_rsi_values.get(sym)
        if r is None or pd.isna(r):
            print(f"{sym}: Not enough data for RSI trend.")
            continue

        if r >= 70:
            trend = f"Overbought / strong momentum (RSI14 = {r:.1f})."
        elif 60 <= r < 70:
            trend = f"Bullish momentum (RSI14 = {r:.1f})."
        elif 40 <= r < 60:
            trend = f"Neutral / range-bound (RSI14 = {r:.1f})."
        elif 30 <= r < 40:
            trend = f"Weak / bearish bias (RSI14 = {r:.1f})."
        else:  # r < 30
            trend = f"Oversold zone (RSI14 = {r:.1f})."

        print(f"{sym}: {trend}")

# ---------- DAY HIGH / LOW / BEST PERFORMER ----------

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
            highs = data["High"][sym].dropna()
            if highs.empty:
                continue
            high_val = highs.iloc[-1]
            print(f"{sym}: High = {high_val:.2f}")
        except Exception:
            continue

def all_day_low():
    print("\nAll stocks - Today Low:")
    data = yf.download(nifty50_symbols, period="1d", group_by="ticker", auto_adjust=False)
    for sym in nifty50_symbols:
        try:
            lows = data["Low"][sym].dropna()
            if lows.empty:
                continue
            low_val = lows.iloc[-1]
            print(f"{sym}: Low = {low_val:.2f}")
        except Exception:
            continue

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
    ch = input("Enter your choice (0‑5): ").strip()
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
    else:
        print("Invalid choice. Try again.")
