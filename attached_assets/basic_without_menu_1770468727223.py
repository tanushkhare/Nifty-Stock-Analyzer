import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# Step 1: Nifty 50 stock symbols (hardcoded)
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

# Step 2: Let user pick a stock (robust input)
print("Nifty 50 Stocks:")
for i, symbol in enumerate(nifty50_symbols, start=1):
    print(f"{i}. {symbol}")

while True:
    user_inp = input("Enter the number of the stock you want to analyze: ").strip()
    if not user_inp:
        print("Please enter a number (do not leave it blank).")
        continue
    if not user_inp.isdigit():
        print("Please enter digits only.")
        continue

    choice = int(user_inp)
    if 1 <= choice <= len(nifty50_symbols):
        break
    else:
        print(f"Please enter a number between 1 and {len(nifty50_symbols)}.")

selected_symbol = nifty50_symbols[choice - 1]
print(f"You selected: {selected_symbol}")

# Step 3: Download historical data
print("Downloading data...")
data = yf.download(selected_symbol, period="6mo", interval="1d", auto_adjust=True)

if data.empty:
    print("No data found for this stock. Try another.")
    raise SystemExit

# Some yfinance versions return (n,1) columns; squeeze to 1‑D Series. [web:32]
close = data["Close"].squeeze()      # becomes shape (n,) even if (n,1)
volume = data["Volume"].squeeze()

# Step 4: Calculate moving averages on the 1‑D Close Series
short_window = 20
long_window = 50
sma20 = close.rolling(window=short_window).mean()
sma50 = close.rolling(window=long_window).mean()   # [web:73]

# Step 5: Plot price + SMAs + volume
fig, (ax_price, ax_vol) = plt.subplots(
    nrows=2,
    ncols=1,
    sharex=True,
    figsize=(12, 8),
    gridspec_kw={"height_ratios": [3, 1]}
)

# Top: price with SMAs
ax_price.plot(close.index, close.values, label="Close", color="black", linewidth=1.5)
ax_price.plot(close.index, sma20.values, label="20-day SMA", color="blue", linewidth=1.2)
ax_price.plot(close.index, sma50.values, label="50-day SMA", color="orange", linewidth=1.2)
ax_price.set_ylabel("Price (INR)")
ax_price.set_title(f"{selected_symbol} Price, Moving Averages & Volume (6M)")
ax_price.legend()
ax_price.grid(alpha=0.3)

# Bottom: volume bars (1‑D arrays, scalar style args) [web:83][web:95]
ax_vol.bar(volume.index, volume.values, color="grey", width=1.0, linewidth=0.0)
ax_vol.set_ylabel("Volume")
ax_vol.set_xlabel("Date")
ax_vol.grid(alpha=0.3)

plt.tight_layout()
plt.show()

# Step 6: Simple buy/sell suggestion
if pd.notna(sma20.iloc[-1]) and pd.notna(sma50.iloc[-1]):
    if sma20.iloc[-1] > sma50.iloc[-1]:
        print("Bullish trend: Consider buying (do more research!).")
    else:
        print("Bearish trend: Not a good time to buy.")
else:
    print("Not enough data for moving average analysis.")
