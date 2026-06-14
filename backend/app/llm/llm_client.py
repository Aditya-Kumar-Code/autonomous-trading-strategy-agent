from __future__ import annotations

import json

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.config import Settings
from app.schemas.signal import SignalDecision


class LLMClient:
	def __init__(self, settings: Settings):
		self.settings = settings
		self.model = None

		if settings.openai_api_key:
			self.model = ChatOpenAI(
				api_key=settings.openai_api_key,
				model=settings.openai_model,
				temperature=0,
			)

		self.prompt = ChatPromptTemplate.from_messages(
			[
				(
					"system",
					"You are a trading analysis assistant. Return only valid JSON that matches the requested schema.",
				),
				(
					"human",
					"Analyze this market snapshot for {ticker} and return a trading decision.\n\nMarket data: {market_data}",
				),
			]
		)

	def generate_signal(self, ticker: str, market_data: dict) -> SignalDecision:
		if self.model is None:
			return self._heuristic_signal(ticker, market_data)

		messages = self.prompt.format_messages(ticker=ticker, market_data=json.dumps(market_data, indent=2))
		response = self.model.invoke(messages)
		payload = self._extract_json(response.content)
		payload.setdefault("ticker", ticker.upper())
		return SignalDecision.model_validate(payload)

	def _heuristic_signal(self, ticker: str, market_data: dict) -> SignalDecision:
		current_price = float(market_data["current_price"])
		avg_price = float(market_data["avg_price"])
		delta = (current_price - avg_price) / avg_price if avg_price else 0.0

		if delta < -0.03:
			action = "BUY"
			rationale = "Price is meaningfully below the monthly average."
		elif delta > 0.03:
			action = "SELL"
			rationale = "Price is meaningfully above the monthly average."
		else:
			action = "HOLD"
			rationale = "Price is close to the monthly average."

		confidence = min(0.95, max(0.55, abs(delta) * 10))

		return SignalDecision(
			ticker=ticker.upper(),
			action=action,
			confidence=confidence,
			rationale=rationale,
			target_price=avg_price * (1.02 if action == "BUY" else 0.98 if action == "SELL" else 1.0),
			stop_loss=avg_price * (0.97 if action == "BUY" else 1.03 if action == "SELL" else 1.0),
		)

	@staticmethod
	def _extract_json(content: str) -> dict:
		if isinstance(content, dict):
			return content

		content = content.strip()
		if content.startswith("```"):
			content = content.strip("`")
			content = content.replace("json\n", "", 1) if content.startswith("json") else content

		return json.loads(content)
