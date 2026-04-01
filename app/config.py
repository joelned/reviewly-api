from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire: int = 30
    refresh_token_expire_days: int = 7
    redis_url: str
    resend_api_key: str
    resend_from_email: str
    environment: str = "development"

    model_config = {"env_file": ".env"}


settings = Settings()
