from fastapi import FastAPI
from app.database import engine
from sqlalchemy import text

app = FastAPI(
    title="ShopSphere Order Service",
    version="1.0.0",
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "order-service",
    }

@app.get("/health/db")
def database_health_check():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {
        "status": "healthy",
        "database": "connected",
    }