from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Autonomous Multi-Agent Support System"
    APP_VERSION: str = "0.1.0"

    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Guard against placeholder secret key in production
        if self.ENVIRONMENT != "development" and self.SECRET_KEY == "your-secret-key-change-in-production":
            raise ValueError(
                "SECURITY ERROR: SECRET_KEY is set to the placeholder value 'your-secret-key-change-in-production'. "
                "This is not safe for production. Please set a secure SECRET_KEY in your environment variables or .env file."
            )

    # LLM Configuration
    LLM_PROVIDER: str = "openai"  # Options: "gemini", "openai"
    GOOGLE_API_KEY: str = ""
    OPENAI_API_KEY: str = "ollama"  # Placeholder for local OpenAI-compatible endpoints
    OPENAI_BASE_URL: str = "http://localhost:11435/v1"  # Local Ollama endpoint
    MODEL_NAME: str = "llama3"  # Default model for local OpenAI-compatible endpoint
    TEMPERATURE: float = 0.2
    MAX_TOKENS: int = 500
    LLM_TIMEOUT_SECONDS: float = 60.0
    LLM_TEST_TIMEOUT_SECONDS: float = 15.0

    # Database Configuration
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/support_system"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    POSTGRES_USER: str = "support_user"
    POSTGRES_PASSWORD: str = "support_password"

    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT Configuration
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Rate Limiting Configuration
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # seconds

    # CORS Configuration
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8080", "http://127.0.0.1:3000", "http://127.0.0.1:8080"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]

    # Workflow Configuration
    ESCALATION_THRESHOLD: float = 0.7  # Confidence threshold below which requests escalate to human review
    KNOWLEDGE_CONFIDENCE_THRESHOLD: float = 0.8  # Confidence threshold for knowledge retrieval

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()