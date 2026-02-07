import { AnalysisResult } from "@/lib/types";
import { Link } from "wouter";
import { cn } from "@/lib/utils";
import { ArrowUpRight, ArrowDownRight, Minus } from "lucide-react";

interface StockTableProps {
  data: AnalysisResult[];
}

export function StockTable({ data }: StockTableProps) {
  return (
    <div className="rounded-md border border-border bg-card overflow-hidden">
      <table className="w-full text-left text-sm">
        <thead className="bg-secondary/50 text-muted-foreground font-heading tracking-wider text-xs">
          <tr>
            <th className="px-4 py-3 font-medium">SYMBOL</th>
            <th className="px-4 py-3 font-medium text-right">PRICE</th>
            <th className="px-4 py-3 font-medium text-right">CHANGE %</th>
            <th className="px-4 py-3 font-medium text-right">RSI (14)</th>
            <th className="px-4 py-3 font-medium text-right">MACD</th>
            <th className="px-4 py-3 font-medium">SIGNAL</th>
            <th className="px-4 py-3 font-medium">RISK</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-border font-mono">
          {data.map((stock) => (
            <tr key={stock.symbol} className="group hover:bg-secondary/30 transition-colors">
              <td className="px-4 py-3 font-bold text-foreground font-sans">
                <Link href={`/stock/${stock.symbol}`} className="hover:text-primary transition-colors">
                  {stock.symbol.replace('.NS', '')}
                </Link>
              </td>
              <td className="px-4 py-3 text-right text-foreground">
                ₹{stock.currentPrice.toLocaleString(undefined, { minimumFractionDigits: 2 })}
              </td>
              <td className={cn("px-4 py-3 text-right flex justify-end items-center gap-1", 
                stock.changePercent >= 0 ? "text-trade-up" : "text-trade-down"
              )}>
                {stock.changePercent >= 0 ? <ArrowUpRight className="w-3 h-3"/> : <ArrowDownRight className="w-3 h-3"/>}
                {Math.abs(stock.changePercent).toFixed(2)}%
              </td>
              <td className={cn("px-4 py-3 text-right font-bold", 
                stock.rsi > 70 ? "text-trade-down" : stock.rsi < 30 ? "text-trade-up" : "text-muted-foreground"
              )}>
                {stock.rsi.toFixed(1)}
              </td>
              <td className="px-4 py-3 text-right text-muted-foreground">
                {stock.macd.line.toFixed(2)}
              </td>
              <td className="px-4 py-3 font-sans text-xs">
                <span className={cn("px-2 py-1 rounded-full border", 
                  stock.signal.includes("Bullish") ? "bg-trade-up/10 text-trade-up border-trade-up/20" :
                  stock.signal.includes("Bearish") ? "bg-trade-down/10 text-trade-down border-trade-down/20" :
                  "bg-secondary text-muted-foreground border-border"
                )}>
                  {stock.signal}
                </span>
              </td>
              <td className="px-4 py-3 font-sans text-xs">
                <span className={cn("font-bold tracking-wide",
                   stock.risk === 'HIGH' ? "text-destructive" :
                   stock.risk === 'MEDIUM' ? "text-trade-neutral" :
                   "text-trade-up"
                )}>
                  {stock.risk}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
