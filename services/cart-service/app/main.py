from fastapi import FastAPI
from app.routes.cart import router as cart_router
from app.routes.cart import internal_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="ShopSphere Cart Service",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cart_router)
app.include_router(internal_router)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "cart-service",
    }