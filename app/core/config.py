from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "credit-ai-backend"
    env: str = "development"
    debug: bool = True

    database_url: str

    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_min: int = 60

    openai_api_key: str
    openai_base_url: str | None = None
    openai_model: str = "gpt-4o-mini"
    openai_max_tokens: int = 600

    tesseract_cmd: str = "/usr/bin/tesseract"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


settings = Settings()
