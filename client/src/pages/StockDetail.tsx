import Layout from "@/components/layout/Layout";
import { analyzeStock, getStockHistory } from "@/lib/mock-data";
import { StockChart } from "@/components/dashboard/StockChart";
import { useRoute } from "wouter";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AlertTriangle, TrendingUp, TrendingDown, Activity, Info } from "lucide-react";
import { cn } from "@/lib/utils";

export default function StockDetail() {
  const [, params] = useRoute("/stock/:symbol");
  const symbol = params?.symbol || "RELIANCE.NS";
  
  const analysis = analyzeStock(symbol);
  const history = getStockHistory(symbol);

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header Section */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 border-b border-border pb-6">
          <div>
            <div className="flex items-center gap-3 mb-1">
               <h1 className="text-4xl font-heading tracking-tight">{symbol.replace('.NS', '')}</h1>
               <span className="bg-secondary px-2 py-1 rounded text-xs font-mono text-muted-foreground">NSE</span>
            </div>
            <div className="flex items-baseline gap-4">
              <span className="text-3xl font-mono font-bold">₹{analysis.currentPrice.toLocaleString()}</span>
              <span className={cn("text-lg font-mono font-medium", analysis.changePercent >= 0 ? "text-trade-up" : "text-trade-down")}>
                {analysis.changePercent >= 0 ? "+" : ""}{analysis.changePercent.toFixed(2)}%
              </span>
            </div>
          </div>

          <div className="flex gap-4">
            <SignalBadge label="TREND" value={analysis.trend} color={analysis.trend === 'BULLISH' ? 'bg-trade-up' : analysis.trend === 'BEARISH' ? 'bg-trade-down' : 'bg-gray-500'} />
            <SignalBadge label="RISK" value={analysis.risk} color={analysis.risk === 'LOW' ? 'bg-trade-up' : analysis.risk === 'HIGH' ? 'bg-destructive' : 'bg-yellow-600'} />
            <div className="flex flex-col items-end justify-center">
                <span className="text-xs font-heading text-muted-foreground">RSI (14)</span>
                <span className={cn("text-xl font-mono font-bold", analysis.rsi > 70 ? "text-destructive" : analysis.rsi < 30 ? "text-trade-up" : "text-foreground")}>
                    {analysis.rsi.toFixed(1)}
                </span>
            </div>
          </div>
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <StockChart data={history} symbol={symbol} />
            
            <Card className="bg-card border-border">
                <CardHeader>
                    <CardTitle className="text-sm font-heading">Indicator Analysis</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <IndicatorBox label="MACD Line" value={analysis.macd.line.toFixed(2)} sub="Above Signal" status="neutral" />
                        <IndicatorBox label="SMA 20" value={analysis.sma.sma20.toFixed(2)} sub="Short Term" status="neutral" />
                        <IndicatorBox label="SMA 50" value={analysis.sma.sma50.toFixed(2)} sub="Long Term" status="neutral" />
                    </div>
                </CardContent>
            </Card>
          </div>

          {/* Sidebar Info */}
          <div className="space-y-6">
             <Card className="bg-secondary/20 border-border">
                <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-primary">
                        <Info className="w-4 h-4" />
                        Scenario Analysis
                    </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="p-4 bg-background/50 rounded-lg border border-border">
                        <div className="text-sm font-bold mb-1">Detected Pattern</div>
                        <div className="text-lg text-primary">{analysis.signal}</div>
                    </div>
                    
                    <div className="space-y-3">
                        <div className="flex justify-between text-sm">
                            <span className="text-muted-foreground">Volume Direction</span>
                            <span className={cn("font-bold", analysis.volume.direction === 'UP' ? "text-trade-up" : "text-trade-down")}>
                                {analysis.volume.direction}
                            </span>
                        </div>
                        <div className="flex justify-between text-sm">
                            <span className="text-muted-foreground">MACD Histogram</span>
                            <span className={cn("font-bold", analysis.macd.histogram > 0 ? "text-trade-up" : "text-trade-down")}>
                                {analysis.macd.histogram.toFixed(3)}
                            </span>
                        </div>
                    </div>
                </CardContent>
             </Card>

             <Card className="bg-card border-border">
                <CardHeader><CardTitle className="text-sm">Strategy Suggestion</CardTitle></CardHeader>
                <CardContent>
                    <p className="text-sm text-muted-foreground leading-relaxed">
                        Based on current {analysis.signal} pattern and RSI at {analysis.rsi.toFixed(1)}, 
                        {analysis.trend === 'BULLISH' ? ' uptrend continuation is likely. Look for pullbacks to SMA20.' : ' downtrend pressure remains. Wait for confirmed reversal.'}
                    </p>
                </CardContent>
             </Card>
          </div>
        </div>
      </div>
    </Layout>
  );
}

function SignalBadge({ label, value, color }: any) {
    return (
        <div className="flex flex-col items-center justify-center min-w-[80px]">
            <span className="text-xs font-heading text-muted-foreground mb-1">{label}</span>
            <span className={cn("px-3 py-0.5 rounded text-xs font-bold text-white", color)}>
                {value}
            </span>
        </div>
    )
}

function IndicatorBox({ label, value, sub, status }: any) {
    return (
        <div className="p-3 border border-border rounded bg-secondary/30">
            <div className="text-xs text-muted-foreground">{label}</div>
            <div className="text-xl font-mono font-bold my-1">{value}</div>
            <div className="text-xs opacity-70">{sub}</div>
        </div>
    )
}
