from fastapi import FastAPI


app = FastAPI(
    title="ShopSphere Inventory Service",
    version="1.0.0",
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "inventory-service",
    }