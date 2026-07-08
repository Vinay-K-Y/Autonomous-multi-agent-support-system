from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Autonomous Multi-Agent Support System"
    APP_VERSION: str = "0.1.0"

    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    LLM_PROVIDER: str = "gemini"

    GOOGLE_API_KEY: str = ""

    MODEL_NAME: str = "gemini-2.5-flash"

    TEMPERATURE: float = 0.2

    MAX_TOKENS: int = 500

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()