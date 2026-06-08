from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SafetyEval Lab"
    environment: str = "development"
    database_url: str = "sqlite:///./safetyeval.db"
    backend_cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    llm_judge_enabled: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]


settings = Settings()
