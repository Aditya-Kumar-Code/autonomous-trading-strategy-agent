from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

	app_name: str = "Autonomous Trading Agent"
	openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
	openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")
	risk_tolerance: float = Field(default=0.5, alias="RISK_TOLERANCE")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
	return Settings()
