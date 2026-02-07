import { NIFTY50_SYMBOLS, StockDataPoint, AnalysisResult } from "./types";
import { calculateRSI, calculateMACD, calculateSMA, classifyScenario } from "./indicators";
import { subDays, format } from "date-fns";

// Seedable random for consistent mock data across reloads
let seed = 1234;
function random() {
  const x = Math.sin(seed++) * 10000;
  return x - Math.floor(x);
}

function generateHistory(symbol: string, days: number = 200): StockDataPoint[] {
  const data: StockDataPoint[] = [];
  let price = 1000 + random() * 2000; // Base price between 1000-3000
  const volatility = 0.02;

  const today = new Date();

  for (let i = days; i >= 0; i--) {
    const date = subDays(today, i);
    const changePercent = (random() - 0.5) * volatility * 2;
    const open = price;
    price = price * (1 + changePercent);
    const close = price;
    const high = Math.max(open, close) * (1 + random() * 0.01);
    const low = Math.min(open, close) * (1 - random() * 0.01);
    const volume = Math.floor(100000 + random() * 900000);

    data.push({
      date: format(date, "yyyy-MM-dd"),
      open, high, low, close, volume
    });
  }
  return data;
}

export const analyzeStock = (symbol: string): AnalysisResult => {
  const history = generateHistory(symbol);
  const closes = history.map(d => d.close);
  const volumes = history.map(d => d.volume);

  const rsiSeries = calculateRSI(closes);
  const macdData = calculateMACD(closes);
  const sma20 = calculateSMA(closes, 20);
  const sma50 = calculateSMA(closes, 50);

  const idx = closes.length - 1;
  const prevIdx = idx - 1;

  const currentRSI = rsiSeries[idx];
  const currentMACD = macdData.macdLine[idx];
  const currentHist = macdData.histogram[idx];
  const prevHist = macdData.histogram[prevIdx];
  const histSlope = currentHist - prevHist;

  const scenario = classifyScenario(currentRSI, currentMACD, histSlope);

  // Trend determination based on SMA
  let trend: 'BULLISH' | 'BEARISH' | 'NEUTRAL' = 'NEUTRAL';
  if (closes[idx] > sma20[idx] && sma20[idx] > sma50[idx]) trend = 'BULLISH';
  else if (closes[idx] < sma20[idx] && sma20[idx] < sma50[idx]) trend = 'BEARISH';

  return {
    symbol,
    currentPrice: closes[idx],
    changePercent: ((closes[idx] - closes[prevIdx]) / closes[prevIdx]) * 100,
    rsi: currentRSI,
    macd: {
      line: currentMACD,
      signal: macdData.signalLine[idx],
      histogram: currentHist
    },
    sma: {
      sma20: sma20[idx],
      sma50: sma50[idx]
    },
    volume: {
      current: volumes[idx],
      avg: volumes.slice(idx - 20, idx).reduce((a, b) => a + b, 0) / 20,
      direction: volumes[idx] > volumes[prevIdx] ? 'UP' : 'DOWN'
    },
    trend,
    signal: scenario.signal,
    risk: scenario.risk
  };
};

export const getAllStocksAnalysis = () => {
  return NIFTY50_SYMBOLS.map(sym => analyzeStock(sym));
};

export const getStockHistory = (symbol: string) => {
    return generateHistory(symbol);
}
