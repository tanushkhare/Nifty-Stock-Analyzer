import { Link, useLocation } from "wouter";
import { LayoutDashboard, LineChart, ScanLine, Search, Settings, Activity } from "lucide-react";
import { cn } from "@/lib/utils";

export default function Layout({ children }: { children: React.ReactNode }) {
  const [location] = useLocation();

  const navItems = [
    { label: "Dashboard", icon: LayoutDashboard, href: "/" },
    { label: "Scanner", icon: ScanLine, href: "/scanner" },
    { label: "Comparison", icon: Activity, href: "/compare" },
  ];

  return (
    <div className="flex h-screen bg-background text-foreground font-sans overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 border-r border-border bg-card flex flex-col">
        <div className="p-6 border-b border-border flex items-center gap-3">
          <div className="w-8 h-8 rounded bg-primary flex items-center justify-center">
            <LineChart className="text-primary-foreground w-5 h-5" />
          </div>
          <h1 className="font-heading text-xl tracking-wider text-foreground">NIFTY<span className="text-primary">PRO</span></h1>
        </div>

        <nav className="flex-1 p-4 space-y-2">
          {navItems.map((item) => (
            <Link key={item.href} href={item.href}>
              <div
                className={cn(
                  "flex items-center gap-3 px-4 py-3 rounded-md transition-all cursor-pointer group hover:bg-accent/50",
                  location === item.href 
                    ? "bg-primary/10 text-primary border-r-2 border-primary" 
                    : "text-muted-foreground"
                )}
              >
                <item.icon className={cn("w-5 h-5", location === item.href ? "text-primary" : "group-hover:text-foreground")} />
                <span className="font-medium">{item.label}</span>
              </div>
            </Link>
          ))}
        </nav>

        <div className="p-4 border-t border-border">
          <div className="bg-secondary/50 p-3 rounded-md border border-border">
            <p className="text-xs text-muted-foreground font-mono">MARKET STATUS</p>
            <div className="flex items-center gap-2 mt-1">
              <span className="w-2 h-2 rounded-full bg-trade-up animate-pulse"></span>
              <span className="text-sm font-bold text-trade-up tracking-wider">LIVE</span>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0">
        <header className="h-16 border-b border-border flex items-center justify-between px-6 bg-background/50 backdrop-blur-md sticky top-0 z-10">
          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            <span className="font-mono text-xs border border-border px-2 py-0.5 rounded">NSE: NIFTY 50</span>
            <span className="h-4 w-px bg-border"></span>
            <span className="font-mono text-xs">UPDATED: {new Date().toLocaleTimeString()}</span>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
              <input 
                type="text" 
                placeholder="Search symbol..." 
                className="bg-secondary/50 border border-border rounded-full py-1.5 pl-9 pr-4 text-sm focus:outline-none focus:ring-1 focus:ring-primary w-64 font-mono placeholder:font-sans"
              />
            </div>
            <button className="p-2 hover:bg-accent rounded-full text-muted-foreground hover:text-foreground">
              <Settings className="w-5 h-5" />
            </button>
          </div>
        </header>

        <div className="flex-1 overflow-auto p-6 scroll-smooth">
          {children}
        </div>
      </main>
    </div>
  );
}
