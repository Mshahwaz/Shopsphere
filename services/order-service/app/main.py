from fastapi import FastAPI

from app.routes.orders import router as orders_router
from app.database import engine
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="ShopSphere Order Service",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(orders_router)

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