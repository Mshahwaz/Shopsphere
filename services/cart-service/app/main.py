from fastapi import FastAPI
from app.routes.cart import router as cart_router

app = FastAPI(
    title="ShopSphere Cart Service",
    version="1.0.0",
)

app.include_router(cart_router)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "cart-service",
    }