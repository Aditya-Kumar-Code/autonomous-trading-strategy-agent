import yfinance as yf


class MarketService:

    def get_stock_data(self, ticker: str) -> dict:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1mo")

        if hist.empty:
            raise ValueError(f"No market data found for ticker '{ticker}'")

        latest_close = float(hist["Close"].iloc[-1])
        average_close = float(hist["Close"].mean())
        price_change_pct = float((hist["Close"].iloc[-1] / hist["Close"].iloc[0] - 1) * 100)

        return {
            "ticker": ticker.upper(),
            "current_price": latest_close,
            "avg_price": average_close,
            "price_change_pct": price_change_pct,
            "recent_high": float(hist["Close"].max()),
            "recent_low": float(hist["Close"].min()),
        }