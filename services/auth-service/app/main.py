from fastapi import FastAPI 
from app.database import engine
from sqlalchemy import text
from app.routes.auth import router as auth_router

app=FastAPI(
    title="ShopSphere Auth Service",
    version="1.0.0"
)
app.include_router(auth_router)

@app.get("/health")
def health_check():
    return {
        "status":"healthy",
        "service":"auth-service"
    }

@app.get("/health/db")
def database_health_check():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": result.scalar(),
        }