from fastapi import FastAPI, HTTPException

from app.agents.trading_agent import TradingAgent
from app.config import get_settings
from app.llm.llm_client import LLMClient
from app.schemas.signal import SignalDecision
from app.services.market_service import MarketService

settings = get_settings()
app = FastAPI(title=settings.app_name)

market_service = MarketService()
llm_client = LLMClient(settings)
trading_agent = TradingAgent(market_service, llm_client)


@app.get("/health")
def health_check() -> dict:
	return {"status": "ok"}


@app.get("/analyze/{ticker}", response_model=SignalDecision)
def analyze_ticker(ticker: str) -> SignalDecision:
	try:
		return trading_agent.analyze(ticker)
	except Exception as exc:
		raise HTTPException(status_code=400, detail=str(exc)) from exc
