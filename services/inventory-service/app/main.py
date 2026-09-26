from fastapi import FastAPI
from app.routes.inventory import router as inventory_router

app = FastAPI(
    title="ShopSphere Inventory Service",
    version="1.0.0",
)

app.include_router(inventory_router)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "inventory-service",
    }