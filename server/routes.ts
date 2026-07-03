import type { Express } from "express";
import type { Server } from "http";

import { getNifty50Data } from "./services/stockService";

export async function registerRoutes(
  httpServer: Server,
  app: Express
): Promise<Server> {

  app.get("/api/stocks", async (_req, res) => {
    try {
      const stocks = await getNifty50Data();
      res.json(stocks);
    } catch (error) {
      console.error(error);
      res.status(500).json({
        message: "Failed to fetch stock data",
      });
    }
  });

  return httpServer;
}
