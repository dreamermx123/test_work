from pathlib import Path
from typing import Literal

from pydantic import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

_env_path = (Path(__file__).parent.parent / ".env").resolve()


class Settings(BaseSettings):
    project_name: str
    port: int
    api_key: str
    mode: Literal["dev", "prod"] = "dev"
    base_url: HttpUrl

    model_config = SettingsConfigDict(
        env_file=[str(_env_path)],
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
