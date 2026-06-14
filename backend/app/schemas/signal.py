from typing import Literal

from pydantic import BaseModel, Field


class SignalDecision(BaseModel):
	ticker: str
	action: Literal["BUY", "SELL", "HOLD"]
	confidence: float = Field(ge=0.0, le=1.0)
	rationale: str
	target_price: float | None = None
	stop_loss: float | None = None
