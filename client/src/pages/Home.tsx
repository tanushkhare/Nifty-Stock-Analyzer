import Layout from "@/components/layout/Layout";
import { StockTable } from "@/components/dashboard/StockTable";
import { getAllStocksAnalysis } from "@/lib/mock-data";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrendingUp, TrendingDown, Activity, AlertCircle } from "lucide-react";
import { useMemo } from "react";
import { cn } from "@/lib/utils";

export default function Home() {
  const allStocks = useMemo(() => getAllStocksAnalysis(), []);
  
  const topGainers = [...allStocks].sort((a, b) => b.changePercent - a.changePercent).slice(0, 5);
  const topLosers = [...allStocks].sort((a, b) => a.changePercent - b.changePercent).slice(0, 5);
  const bullishCount = allStocks.filter(s => s.signal.includes("Bullish")).length;
  const bearishCount = allStocks.filter(s => s.signal.includes("Bearish")).length;

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <StatCard 
            title="Bullish Signals" 
            value={bullishCount} 
            icon={TrendingUp} 
            color="text-trade-up" 
            subtext="Strong buy opportunities"
          />
          <StatCard 
            title="Bearish Signals" 
            value={bearishCount} 
            icon={TrendingDown} 
            color="text-trade-down" 
            subtext="Potential short setups"
          />
          <StatCard 
            title="Market Volatility" 
            value="MED" 
            icon={Activity} 
            color="text-trade-neutral" 
            subtext="VIX: 14.2"
          />
          <StatCard 
            title="Alerts" 
            value={allStocks.filter(s => s.rsi > 70 || s.rsi < 30).length} 
            icon={AlertCircle} 
            color="text-primary" 
            subtext="Overbought / Oversold"
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Top Gainers - 1 Col */}
          <div className="space-y-6">
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="text-sm font-heading tracking-wider text-muted-foreground uppercase">Top Gainers</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {topGainers.map(s => (
                  <div key={s.symbol} className="flex items-center justify-between border-b border-border/50 last:border-0 pb-2 last:pb-0">
                    <div>
                      <div className="font-bold text-sm">{s.symbol.replace('.NS', '')}</div>
                      <div className="text-xs text-muted-foreground">₹{s.currentPrice.toFixed(2)}</div>
                    </div>
                    <div className="text-trade-up font-mono font-bold">+{s.changePercent.toFixed(2)}%</div>
                  </div>
                ))}
              </CardContent>
            </Card>

            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="text-sm font-heading tracking-wider text-muted-foreground uppercase">Top Losers</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {topLosers.map(s => (
                  <div key={s.symbol} className="flex items-center justify-between border-b border-border/50 last:border-0 pb-2 last:pb-0">
                    <div>
                      <div className="font-bold text-sm">{s.symbol.replace('.NS', '')}</div>
                      <div className="text-xs text-muted-foreground">₹{s.currentPrice.toFixed(2)}</div>
                    </div>
                    <div className="text-trade-down font-mono font-bold">{s.changePercent.toFixed(2)}%</div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Market Scanner - 2 Cols */}
          <div className="lg:col-span-2">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-heading">Live Market Scan</h2>
              <div className="flex gap-2">
                <span className="text-xs font-mono bg-secondary px-2 py-1 rounded text-muted-foreground">RSI & MACD FILTER ENABLED</span>
              </div>
            </div>
            <StockTable data={allStocks} />
          </div>
        </div>
      </div>
    </Layout>
  );
}

function StatCard({ title, value, icon: Icon, color, subtext }: any) {
  return (
    <Card className="bg-card border-border">
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs font-heading text-muted-foreground tracking-widest">{title}</p>
            <h3 className={cn("text-3xl font-mono font-bold mt-2", color)}>{value}</h3>
          </div>
          <div className={cn("p-3 rounded-full bg-secondary/50", color)}>
            <Icon className="w-6 h-6" />
          </div>
        </div>
        <p className="text-xs text-muted-foreground mt-4 border-t border-border pt-2">{subtext}</p>
      </CardContent>
    </Card>
  )
}
