import Layout from "@/components/layout/Layout";
import { getStockHistory } from "@/lib/mock-data";
import { NIFTY50_SYMBOLS } from "@/lib/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, Legend, CartesianGrid } from "recharts";
import { useState, useMemo } from "react";
import { format } from "date-fns";
import { Check, Plus } from "lucide-react";
import { cn } from "@/lib/utils";

export default function Comparison() {
  const [selectedStocks, setSelectedStocks] = useState<string[]>(["RELIANCE.NS", "HDFCBANK.NS", "INFY.NS"]);
  
  // Generate comparison data
  // We need to normalize data to start at 0%
  const chartData = useMemo(() => {
     // Get history for all selected stocks
     const histories = selectedStocks.map(sym => {
        const history = getStockHistory(sym);
        const startPrice = history[0].close;
        return {
            symbol: sym,
            data: history.map(d => ({
                date: d.date,
                // Normalized % change
                value: ((d.close - startPrice) / startPrice) * 100
            }))
        }
     });

     // Merge into one array of objects keyed by date
     if (histories.length === 0) return [];
     
     const merged = histories[0].data.map((d, i) => {
        const point: any = { date: d.date };
        histories.forEach(h => {
            point[h.symbol] = h.data[i]?.value || 0;
        });
        return point;
     });
     
     return merged;
  }, [selectedStocks]);

  const toggleStock = (sym: string) => {
    if (selectedStocks.includes(sym)) {
        setSelectedStocks(selectedStocks.filter(s => s !== sym));
    } else {
        if (selectedStocks.length < 5) {
            setSelectedStocks([...selectedStocks, sym]);
        }
    }
  }

  const colors = ["#3b82f6", "#ef4444", "#10b981", "#f59e0b", "#8b5cf6"];

  return (
    <Layout>
      <div className="space-y-6">
        <h1 className="text-2xl font-heading tracking-wide">Performance Comparison (6M)</h1>
        
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            <Card className="bg-card border-border lg:col-span-3 h-[500px]">
                <CardHeader>
                    <CardTitle className="text-sm font-heading">Normalized Returns (%)</CardTitle>
                </CardHeader>
                <CardContent className="h-[420px] pt-0">
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={chartData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="hsl(217 32% 20%)" />
                            <XAxis 
                                dataKey="date" 
                                tick={{fill: 'hsl(215 20% 65%)', fontSize: 10}}
                                tickFormatter={(val) => format(new Date(val), 'MMM dd')}
                            />
                            <YAxis 
                                tick={{fill: 'hsl(215 20% 65%)', fontSize: 10}}
                                tickFormatter={(val) => `${val.toFixed(0)}%`}
                            />
                            <Tooltip 
                                contentStyle={{ backgroundColor: 'hsl(222 47% 13%)', borderColor: 'hsl(217 32% 20%)' }}
                                itemStyle={{ fontSize: 12, fontFamily: 'monospace' }}
                            />
                            <Legend />
                            {selectedStocks.map((sym, i) => (
                                <Line 
                                    key={sym}
                                    type="monotone" 
                                    dataKey={sym} 
                                    name={sym.replace('.NS', '')}
                                    stroke={colors[i % colors.length]} 
                                    strokeWidth={2}
                                    dot={false}
                                />
                            ))}
                        </LineChart>
                    </ResponsiveContainer>
                </CardContent>
            </Card>

            {/* Selector */}
            <Card className="bg-card border-border">
                <CardHeader>
                    <CardTitle className="text-sm font-heading">Select Stocks (Max 5)</CardTitle>
                </CardHeader>
                <CardContent className="h-[420px] overflow-y-auto pr-2">
                    <div className="space-y-2">
                        {NIFTY50_SYMBOLS.map((sym: string) => {
                            const isSelected = selectedStocks.includes(sym);
                            return (
                                <button 
                                    key={sym}
                                    onClick={() => toggleStock(sym)}
                                    className={cn(
                                        "w-full flex items-center justify-between px-3 py-2 rounded text-xs font-mono transition-colors",
                                        isSelected 
                                            ? "bg-primary/20 text-primary border border-primary/50" 
                                            : "hover:bg-secondary text-muted-foreground"
                                    )}
                                >
                                    {sym.replace('.NS', '')}
                                    {isSelected ? <Check className="w-3 h-3" /> : <Plus className="w-3 h-3 opacity-50"/>}
                                </button>
                            )
                        })}
                    </div>
                </CardContent>
            </Card>
        </div>
      </div>
    </Layout>
  );
}
