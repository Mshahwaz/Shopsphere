from fastapi import FastAPI
from app.routes.products import router as product_router

app = FastAPI(
    title="Shopsphere Product service",
    version="1.0.0"
)

app.include_router(product_router)

@app.get("/health")
def health_check():
    return {
        "status":"healthy",
        "service": "product-service"
    }