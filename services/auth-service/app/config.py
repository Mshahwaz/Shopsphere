from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_host: str
    database_port: int
    database_name: str
    database_user: str
    database_password: str

    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30

    
    user_service_url: str
    user_service_auth_token: str

    refresh_token_expire_days: int = 7
    refresh_token_cookie_name: str = "refresh_token"
    refresh_token_cookie_secure: bool = False
    refresh_token_cookie_httponly: bool = True
    refresh_token_cookie_samesite: str = "lax"

    model_config= SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings=Settings()