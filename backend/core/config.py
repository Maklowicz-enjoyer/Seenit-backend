from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24      # token ważny 24h

    model_config = SettingsConfigDict(env_file="secrets/.env", extra="ignore")

settings = Settings()