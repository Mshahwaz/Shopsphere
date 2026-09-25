from fastapi import FastAPI

app = FastAPI(
    title="Shopsphere Product service",
    version="1.0.0"
)

@app.get("/health")
def health_check():
    return {
        "status":"healthy",
        "service": "product-service"
    }