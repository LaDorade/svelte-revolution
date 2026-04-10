from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve .env.local relative to the repo root so `pnpm ia` (which cds into
# ia_server/) still picks up the project-root env file where DB_URL,
# MISTRAL_API_KEY, PB_BOT_EMAIL, PB_BOT_PASSWORD live.
_REPO_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
	model_config = SettingsConfigDict(
		env_file=(_REPO_ROOT / ".env.local", ".env.local"),
		env_file_encoding="utf-8",
		extra="ignore",
	)

	db_url: str = "http://localhost:8090"
	# Optional at import time so tests can run without env vars; service startup
	# will log a clear error if these are missing when login is attempted.
	pb_bot_email: str = ""
	pb_bot_password: str = ""

	mistral_api_key: str = ""
	mistral_model: str = "mistral-small-latest"
	mistral_timeout_s: float = 15.0

	worker_count: int = 2


settings = Settings()  # type: ignore[call-arg]
