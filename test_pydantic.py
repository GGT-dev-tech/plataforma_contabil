from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgres://bad"

settings = Settings()
settings.DATABASE_URL = settings.DATABASE_URL.replace("postgres://", "postgresql+psycopg://")
print(settings.DATABASE_URL)
