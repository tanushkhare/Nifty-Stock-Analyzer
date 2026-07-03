import Layout from "@/components/layout/Layout";
import { StockTable } from "@/components/dashboard/StockTable";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrendingUp, TrendingDown, Activity, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import { useQuery } from "@tanstack/react-query";

export default function Home() {
  const { data: rawStocks = [] as any[] } = useQuery({
    queryKey: ["stocks"],
    queryFn: async () => {
      const res = await fetch("/api/stocks");

      if (!res.ok) {
        throw new Error("Failed to fetch stocks");
      }

      return res.json();
    },
    refetchInterval: 60000,
  });

  const allStocks = rawStocks.map((stock: any) => ({
    symbol: stock.symbol,
    currentPrice: stock.price,
    changePercent: stock.change,

    rsi: 50,

    macd: {
      line: 0,
      signal: 0,
      histogram: 0,
    },

    trend: stock.change >= 0 ? "BULLISH" : "BEARISH",

    signal:
      stock.change > 1
        ? "Bullish Momentum"
        : stock.change < -1
        ? "Bearish Momentum"
        : "Neutral",

    risk:
      Math.abs(stock.change) > 3
        ? "HIGH"
        : Math.abs(stock.change) > 1
        ? "MEDIUM"
        : "LOW",
  }));

  const topGainers = [...allStocks]
    .sort((a: any, b: any) => b.changePercent - a.changePercent)
    .slice(0, 5);

  const topLosers = [...allStocks]
    .sort((a: any, b: any) => a.changePercent - b.changePercent)
    .slice(0, 5);

  const bullishCount = allStocks.filter(
    (s: any) => s.signal.includes("Bullish")
  ).length;

  const bearishCount = allStocks.filter(
    (s: any) => s.signal.includes("Bearish")
  ).length;

  const alertsCount = allStocks.filter(
    (s: any) => Math.abs(s.changePercent) > 3
  ).length;

  return (
    <Layout>
      <div className="space-y-6">
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
            title="Market Status"
            value="LIVE"
            icon={Activity}
            color="text-trade-neutral"
            subtext="Yahoo Finance Feed"
          />

          <StatCard
            title="Alerts"
            value={alertsCount}
            icon={AlertCircle}
            color="text-primary"
            subtext="High movement stocks"
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="space-y-6">
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="text-sm font-heading tracking-wider text-muted-foreground uppercase">
                  Top Gainers
                </CardTitle>
              </CardHeader>

              <CardContent className="space-y-4">
                {topGainers.map((s: any) => (
                  <div
                    key={s.symbol}
                    className="flex items-center justify-between border-b border-border/50 last:border-0 pb-2 last:pb-0"
                  >
                    <div>
                      <div className="font-bold text-sm">
                        {s.symbol.replace(".NS", "")}
                      </div>

                      <div className="text-xs text-muted-foreground">
                        ₹{Number(s.currentPrice).toFixed(2)}
                      </div>
                    </div>

                    <div className="text-trade-up font-mono font-bold">
                      {s.changePercent > 0 ? "+" : ""}
                      {Number(s.changePercent).toFixed(2)}%
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="text-sm font-heading tracking-wider text-muted-foreground uppercase">
                  Top Losers
                </CardTitle>
              </CardHeader>

              <CardContent className="space-y-4">
                {topLosers.map((s: any) => (
                  <div
                    key={s.symbol}
                    className="flex items-center justify-between border-b border-border/50 last:border-0 pb-2 last:pb-0"
                  >
                    <div>
                      <div className="font-bold text-sm">
                        {s.symbol.replace(".NS", "")}
                      </div>

                      <div className="text-xs text-muted-foreground">
                        ₹{Number(s.currentPrice).toFixed(2)}
                      </div>
                    </div>

                    <div className="text-trade-down font-mono font-bold">
                      {Number(s.changePercent).toFixed(2)}%
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          <div className="lg:col-span-2">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-heading">
                Live Market Scan
              </h2>

              <span className="text-xs font-mono bg-secondary px-2 py-1 rounded text-muted-foreground">
                LIVE YAHOO FINANCE DATA
              </span>
            </div>

            <StockTable data={allStocks as any} />
          </div>
        </div>
      </div>
    </Layout>
  );
}

function StatCard({
  title,
  value,
  icon: Icon,
  color,
  subtext,
}: any) {
  return (
    <Card className="bg-card border-border">
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs font-heading text-muted-foreground tracking-widest">
              {title}
            </p>

            <h3
              className={cn(
                "text-3xl font-mono font-bold mt-2",
                color
              )}
            >
              {value}
            </h3>
          </div>

          <div
            className={cn(
              "p-3 rounded-full bg-secondary/50",
              color
            )}
          >
            <Icon className="w-6 h-6" />
          </div>
        </div>

        <p className="text-xs text-muted-foreground mt-4 border-t border-border pt-2">
          {subtext}
        </p>
      </CardContent>
    </Card>
  );
}