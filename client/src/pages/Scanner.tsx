import Layout from "@/components/layout/Layout";
import { StockTable } from "@/components/dashboard/StockTable";
import { getAllStocksAnalysis } from "@/lib/mock-data";
import { useState, useMemo } from "react";
import { Filter, SlidersHorizontal } from "lucide-react";

export default function Scanner() {
  const allStocks = useMemo(() => getAllStocksAnalysis(), []);
  const [filter, setFilter] = useState<'ALL' | 'BULLISH' | 'BEARISH' | 'OVERSOLD' | 'OVERBOUGHT'>('ALL');

  const filteredData = allStocks.filter(stock => {
    if (filter === 'ALL') return true;
    if (filter === 'BULLISH') return stock.signal.includes('Bullish') || stock.trend === 'BULLISH';
    if (filter === 'BEARISH') return stock.signal.includes('Bearish') || stock.trend === 'BEARISH';
    if (filter === 'OVERSOLD') return stock.rsi < 30;
    if (filter === 'OVERBOUGHT') return stock.rsi > 70;
    return true;
  });

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-heading tracking-wide">Advanced Scanner</h1>
            <p className="text-muted-foreground text-sm">Real-time filtering based on RSI(14), MACD(12,26,9) and Price Action.</p>
          </div>
          
          <div className="flex items-center gap-2 bg-card border border-border p-1 rounded-lg">
            <FilterButton label="All" active={filter === 'ALL'} onClick={() => setFilter('ALL')} />
            <div className="w-px h-4 bg-border mx-1" />
            <FilterButton label="Bullish" active={filter === 'BULLISH'} onClick={() => setFilter('BULLISH')} color="text-trade-up" />
            <FilterButton label="Bearish" active={filter === 'BEARISH'} onClick={() => setFilter('BEARISH')} color="text-trade-down" />
            <div className="w-px h-4 bg-border mx-1" />
            <FilterButton label="Oversold (<30)" active={filter === 'OVERSOLD'} onClick={() => setFilter('OVERSOLD')} />
            <FilterButton label="Overbought (>70)" active={filter === 'OVERBOUGHT'} onClick={() => setFilter('OVERBOUGHT')} />
          </div>
        </div>

        <div className="grid grid-cols-1 gap-6">
          <StockTable data={filteredData} />
        </div>
      </div>
    </Layout>
  );
}

function FilterButton({ label, active, onClick, color }: any) {
  return (
    <button 
      onClick={onClick}
      className={cn(
        "px-4 py-1.5 rounded-md text-sm font-medium transition-all",
        active ? "bg-primary text-primary-foreground shadow-sm" : "text-muted-foreground hover:text-foreground hover:bg-secondary",
        color && !active && color
      )}
    >
      {label}
    </button>
  );
}

import { cn } from "@/lib/utils";
