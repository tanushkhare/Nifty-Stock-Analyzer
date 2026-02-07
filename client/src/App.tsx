import { Switch, Route } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import NotFound from "@/pages/not-found";
import Home from "@/pages/Home";
import Scanner from "@/pages/Scanner";
import StockDetail from "@/pages/StockDetail";
import Comparison from "@/pages/Comparison";

function Router() {
  return (
    <Switch>
      <Route path="/" component={Home} />
      <Route path="/scanner" component={Scanner} />
      <Route path="/stock/:symbol" component={StockDetail} />
      <Route path="/compare" component={Comparison} />
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Router />
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;
