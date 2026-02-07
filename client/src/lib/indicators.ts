import { StockDataPoint } from "./types";

/**
 * Calculates Simple Moving Average (SMA)
 */
export function calculateSMA(data: number[], period: number): number[] {
  const sma = [];
  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) {
      sma.push(NaN);
      continue;
    }
    const slice = data.slice(i - period + 1, i + 1);
    const sum = slice.reduce((a, b) => a + b, 0);
    sma.push(sum / period);
  }
  return sma;
}

/**
 * Calculates RSI (Relative Strength Index)
 */
export function calculateRSI(prices: number[], period: number = 14): number[] {
  const rsi = [];
  const gains = [];
  const losses = [];

  // Calculate changes
  for (let i = 1; i < prices.length; i++) {
    const change = prices[i] - prices[i - 1];
    gains.push(Math.max(0, change));
    losses.push(Math.max(0, -change));
  }

  // Initial Average Gain/Loss
  let avgGain = gains.slice(0, period).reduce((a, b) => a + b, 0) / period;
  let avgLoss = losses.slice(0, period).reduce((a, b) => a + b, 0) / period;

  // First RSI
  rsi.push(NaN); // For index 0
  for(let i=1; i<period; i++) rsi.push(NaN); // Fill until period

  let rs = avgGain / avgLoss;
  rsi.push(100 - (100 / (1 + rs)));

  // Smoothed averages for subsequent values
  for (let i = period; i < gains.length; i++) {
    avgGain = ((avgGain * (period - 1)) + gains[i]) / period;
    avgLoss = ((avgLoss * (period - 1)) + losses[i]) / period;
    rs = avgGain / avgLoss;
    rsi.push(100 - (100 / (1 + rs)));
  }

  // Pad the beginning to match prices length ( RSI array is shorter by 1 because of diff)
  // Actually, standard RSI usually aligns with the price array length, first 'period' values are NaN.
  return rsi;
}

/**
 * Calculates MACD (Moving Average Convergence Divergence)
 */
export function calculateMACD(prices: number[], fast: number = 12, slow: number = 26, signal: number = 9) {
  const emaFast = calculateEMA(prices, fast);
  const emaSlow = calculateEMA(prices, slow);
  
  const macdLine = prices.map((_, i) => emaFast[i] - emaSlow[i]);
  const signalLine = calculateEMA(macdLine, signal);
  const histogram = macdLine.map((val, i) => val - signalLine[i]);

  return { macdLine, signalLine, histogram };
}

function calculateEMA(data: number[], period: number): number[] {
  const k = 2 / (period + 1);
  const ema = [data[0]]; // Start with first price as approximation or use SMA for first few
  for (let i = 1; i < data.length; i++) {
    ema.push(data[i] * k + ema[i - 1] * (1 - k));
  }
  return ema;
}

/**
 * Ported Classification Logic from Python
 */
export function classifyScenario(rsiVal: number, macdVal: number, histSlope: number): { signal: string, risk: 'LOW' | 'MEDIUM' | 'HIGH' } {
  if (isNaN(rsiVal) || isNaN(macdVal) || isNaN(histSlope)) {
    return { signal: "Not enough data", risk: 'MEDIUM' };
  }

  if (rsiVal >= 55 && rsiVal <= 70 && macdVal > 0 && histSlope > 0) {
    return { signal: "Strong Bullish (Long Build)", risk: 'LOW' };
  }
  if (rsiVal >= 40 && rsiVal < 55 && macdVal > 0 && Math.abs(histSlope) < 0.05) {
    return { signal: "Short Covering (Weak Rally)", risk: 'MEDIUM' };
  }
  if (rsiVal >= 60 && rsiVal <= 75 && macdVal > 0 && Math.abs(histSlope) < 0.1) {
    return { signal: "Quiet Accumulation", risk: 'MEDIUM' };
  }
  if (rsiVal >= 45 && rsiVal <= 60 && macdVal > 0 && histSlope < 0) {
    return { signal: "Profit-Taking / Reversal", risk: 'HIGH' };
  }
  if (rsiVal >= 20 && rsiVal <= 40 && macdVal < 0 && histSlope < 0) {
    return { signal: "Strong Bearish (Short Build)", risk: 'LOW' }; // Low risk for shorts
  }
  if (rsiVal >= 20 && rsiVal <= 35 && macdVal < 0 && histSlope > 0) {
    return { signal: "Liquidation / Panic Washout", risk: 'HIGH' };
  }
  
  if (rsiVal > 70) return { signal: "Overbought", risk: 'HIGH' };
  if (rsiVal < 30) return { signal: "Oversold", risk: 'HIGH' };

  return { signal: "Neutral / Range-bound", risk: 'MEDIUM' };
}
