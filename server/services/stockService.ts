import YahooFinance from "yahoo-finance2";

const yahooFinance = new YahooFinance();
export async function getQuote(symbol: string) {
  try {
    const quote = await yahooFinance.quote(symbol);

    return {
      symbol: quote.symbol,
      price: quote.regularMarketPrice,
      change: quote.regularMarketChangePercent,
      volume: quote.regularMarketVolume,
      marketState: quote.marketState,
    };
  } catch (error) {
    console.error(`Error fetching ${symbol}`, error);

    return {
      symbol,
      price: 0,
      change: 0,
      volume: 0,
      marketState: "UNKNOWN",
    };
  }
}

export async function getNifty50Data() {
  const symbols = [
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "SBIN.NS",
    "ITC.NS",
    "AXISBANK.NS",
    "LT.NS",
    "BHARTIARTL.NS",
  ];

  const results = await Promise.all(
    symbols.map((symbol) => getQuote(symbol))
  );

  return results;
}