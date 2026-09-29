from fastapi import FastAPI
from sqlalchemy import text

from app.database import engine
from app.routes.payments import router as payments_router


app = FastAPI(
    title="ShopSphere Payment Service",
    version="1.0.0",
)


app.include_router(payments_router)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "payment-service",
    }


@app.get("/health/db")
def database_health_check():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {
        "status": "healthy",
        "database": "connected",
    }