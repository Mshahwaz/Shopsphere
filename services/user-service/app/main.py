from fastapi import FastAPI
from app.routes.users import router as users_router
from fastapi.middleware.cors import CORSMiddleware


app=FastAPI(
    title="Shopsphere User Service",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(users_router)

@app.get("/health")
def health_check():
    return {
        "status":"healthy",
        "service":"user-service"
    }