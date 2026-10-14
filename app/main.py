from fastapi import FastAPI

app = FastAPI() # initializer to FastAPI

@app.get("/health") # Create slug to run health check
def health_check():
    return {
        "status": "healthy",
        "service": "BeaconKeep"
    }

