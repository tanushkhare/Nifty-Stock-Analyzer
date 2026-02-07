import { Area, AreaChart, Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis, ComposedChart, Line } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { StockDataPoint } from "@/lib/types";
import { format } from "date-fns";

interface StockChartProps {
  data: StockDataPoint[];
  symbol: string;
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-card border border-border p-3 rounded shadow-xl font-mono text-xs z-50">
        <p className="text-muted-foreground mb-1">{label}</p>
        {payload.map((p: any) => (
          <div key={p.name} className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full" style={{ backgroundColor: p.color }}></span>
            <span className="text-muted-foreground capitalize">{p.name}:</span>
            <span className="text-foreground font-bold">
              {p.value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </span>
          </div>
        ))}
      </div>
    );
  }
  return null;
};

export function StockChart({ data, symbol }: StockChartProps) {
  // Calculate SMA manually for the chart if needed, or assume data has it. 
  // Ideally, mock-data should provide it or we compute it here.
  // For visual simplicity, let's just render Price vs Volume for now in this main chart.
  
  return (
    <Card className="h-[500px] flex flex-col border-border bg-card/50">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="font-heading tracking-wide text-lg text-foreground flex items-center gap-2">
          {symbol} <span className="text-sm font-sans font-normal text-muted-foreground">Price Action & Volume</span>
        </CardTitle>
        <div className="flex gap-2">
            {['1D', '1W', '1M', '3M', '6M', '1Y'].map(tf => (
                <button key={tf} className={`px-2 py-0.5 text-xs rounded ${tf === '6M' ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:bg-accent'}`}>
                    {tf}
                </button>
            ))}
        </div>
      </CardHeader>
      <CardContent className="flex-1 min-h-0 pt-0">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data}>
            <defs>
              <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="hsl(217 91% 60%)" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="hsl(217 91% 60%)" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(217 32% 20%)" vertical={false} />
            <XAxis 
                dataKey="date" 
                tick={{fill: 'hsl(215 20% 65%)', fontSize: 10, fontFamily: 'JetBrains Mono'}}
                tickFormatter={(val) => format(new Date(val), 'MMM dd')}
                minTickGap={30}
                axisLine={false}
                tickLine={false}
            />
            <YAxis 
                yAxisId="right"
                orientation="right"
                domain={['auto', 'auto']}
                tick={{fill: 'hsl(215 20% 65%)', fontSize: 10, fontFamily: 'JetBrains Mono'}}
                axisLine={false}
                tickLine={false}
                tickFormatter={(val) => `₹${val.toFixed(0)}`}
            />
            <YAxis 
                yAxisId="left"
                orientation="left"
                tick={{fill: 'hsl(215 20% 65%)', fontSize: 10, fontFamily: 'JetBrains Mono'}}
                axisLine={false}
                tickLine={false}
                tickFormatter={(val) => `${(val/1000000).toFixed(1)}M`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Bar yAxisId="left" dataKey="volume" fill="hsl(217 32% 25%)" opacity={0.5} barSize={2} />
            <Area 
                yAxisId="right"
                type="monotone" 
                dataKey="close" 
                stroke="hsl(217 91% 60%)" 
                strokeWidth={2}
                fillOpacity={1} 
                fill="url(#colorPrice)" 
            />
          </ComposedChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
