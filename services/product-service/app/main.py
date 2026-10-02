from fastapi import FastAPI, Depends
from app.routes.products import router as product_router
from app.routes.categories import router as category_router

from app.security import get_current_user, require_role

app = FastAPI(
    title="Shopsphere Product service",
    version="1.0.0"
)

app.include_router(product_router)
app.include_router(category_router)

@app.get("/health")
def health_check():
    return {
        "status":"healthy",
        "service": "product-service"
    }

