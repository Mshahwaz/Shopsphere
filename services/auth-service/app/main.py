from fastapi import FastAPI 

app=FastAPI(
    title="ShopSphere Auth Service",
    version="1.0.0"
)

@app.get("/health")
def health_check():
    return {
        "status":"healthy",
        "service":"auth-service"
    }