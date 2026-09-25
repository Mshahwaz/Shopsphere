from fastapi import FastAPI
from app.routes.users import router as users_router
app=FastAPI(
    title="Shopsphere User Service",
    version="1.0.0"
)
app.include_router(users_router)

@app.get("/health")
def health_check():
    return {
        "status":"healthy",
        "service":"user-service"
    }