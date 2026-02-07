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

def print_menu():
    print("\n" + "="*60)
    print("          NIFTY 50 ANALYZER")
    print("="*60)
    print("1. Single Stock Analysis (chart + SMA + volume)")
    print("2. Multiple Stock Comparison (3M % performance)")
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

    fig, (ax_price, ax_vol) = plt.subplots(
        nrows=2, ncols=1, sharex=True, figsize=(12, 8),
        gridspec_kw={"height_ratios": [3, 1]}
    )

    ax_price.plot(close.index, close.values, label="Close", color="black", linewidth=1.5)
    ax_price.plot(close.index, sma20.values, label="20-day SMA", color="blue", linewidth=1.2)
    ax_price.plot(close.index, sma50.values, label="50-day SMA", color="orange", linewidth=1.2)
    ax_price.set_ylabel("Price (INR)")
    ax_price.set_title(f"{symbol} Price, Moving Averages & Volume (6M)")
    ax_price.legend()
    ax_price.grid(alpha=0.3)

    ax_vol.bar(volume.index, volume.values, color="grey", width=1.0, linewidth=0.0)
    ax_vol.set_ylabel("Volume")
    ax_vol.set_xlabel("Date")
    ax_vol.grid(alpha=0.3)

    plt.tight_layout()
    plt.show()

    if pd.notna(sma20.iloc[-1]) and pd.notna(sma50.iloc[-1]):
        if sma20.iloc[-1] > sma50.iloc[-1]:
            print("Bullish trend: Consider buying (do more research!).")
        else:
            print("Bearish trend: Not a good time to buy.")
    else:
        print("Not enough data for moving average analysis.")

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

    data = yf.download(syms, period="3mo", interval="1d")["Close"]
    norm = (data / data.iloc[0] - 1) * 100.0

    plt.figure(figsize=(12, 7))
    for s in syms:
        plt.plot(norm.index, norm[s].values, label=s.replace(".NS",""), linewidth=1.5)
    plt.title("3‑Month % Performance")
    plt.xlabel("Date")
    plt.ylabel("% Change from Start")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()

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
