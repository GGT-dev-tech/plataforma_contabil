from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_ENV: str = "development"
    APP_NAME: str = "plataforma-contabil"
    SECRET_KEY: str = "supersecret"
    JWT_SECRET_KEY: str = "supersecretjwt"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60
    DATABASE_URL: str = "sqlite:///./canonical.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    UPLOAD_STORAGE: str = "local"
    UPLOAD_PATH: str = "/app/uploads"
    CORS_ORIGINS: list | str = ["http://localhost:5173", "https://frontend-staging.up.railway.app"]
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"

settings = Settings()
