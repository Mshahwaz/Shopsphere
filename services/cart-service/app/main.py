from fastapi import FastAPI
from app.routes.cart import router as cart_router
from app.routes.cart import internal_router

app = FastAPI(
    title="ShopSphere Cart Service",
    version="1.0.0",
)

app.include_router(cart_router)
app.include_router(internal_router)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "cart-service",
    }