// Nifty 50 Symbols
export const NIFTY50_SYMBOLS = [
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
];

export interface StockDataPoint {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface AnalysisResult {
  symbol: string;
  currentPrice: number;
  changePercent: number;
  rsi: number;
  macd: {
    line: number;
    signal: number;
    histogram: number;
  };
  sma: {
    sma20: number;
    sma50: number;
  };
  volume: {
    current: number;
    avg: number;
    direction: 'UP' | 'DOWN';
  };
  trend: 'BULLISH' | 'BEARISH' | 'NEUTRAL';
  signal: string;
  risk: 'LOW' | 'MEDIUM' | 'HIGH';
}
