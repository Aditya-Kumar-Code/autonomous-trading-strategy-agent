from __future__ import annotations

from typing import TypedDict

from langgraph.graph import END, StateGraph

from app.llm.llm_client import LLMClient
from app.schemas.signal import SignalDecision
from app.services.market_service import MarketService


class TradingState(TypedDict, total=False):
	ticker: str
	market_data: dict
	signal: SignalDecision


class TradingAgent:
	def __init__(self, market_service: MarketService, llm_client: LLMClient):
		self.market_service = market_service
		self.llm_client = llm_client
		self.graph = self._build_graph()

	def _build_graph(self):
		graph = StateGraph(TradingState)

		graph.add_node("fetch_market_data", self._fetch_market_data)
		graph.add_node("analyze", self._analyze)

		graph.set_entry_point("fetch_market_data")
		graph.add_edge("fetch_market_data", "analyze")
		graph.add_edge("analyze", END)

		return graph.compile()

	def _fetch_market_data(self, state: TradingState) -> TradingState:
		ticker = state["ticker"]
		return {"ticker": ticker, "market_data": self.market_service.get_stock_data(ticker)}

	def _analyze(self, state: TradingState) -> TradingState:
		ticker = state["ticker"]
		market_data = state["market_data"]
		signal = self.llm_client.generate_signal(ticker, market_data)
		return {"signal": signal}

	def analyze(self, ticker: str) -> SignalDecision:
		result = self.graph.invoke({"ticker": ticker})
		return result["signal"]
