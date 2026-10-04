from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_host: str
    database_port: int
    database_name: str
    database_user: str
    database_password: str

    jwt_secret: str
    jwt_algorithm: str = "HS256"

    model_config= SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings=Settings()