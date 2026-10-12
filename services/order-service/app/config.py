from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_host: str
    database_port: int
    database_name: str
    database_user: str
    database_password: str

    product_service_url: str
    inventory_service_url: str
    payment_service_url: str
    cart_service_url: str

    inventory_service_auth_token: str
    payment_service_auth_token: str
    cart_service_auth_token: str

    jwt_secret: str
    jwt_algorithm: str
    
    aws_region: str = "us-east-1"
    sqs_endpoint_url: str | None = None
    sqs_queue_url: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()