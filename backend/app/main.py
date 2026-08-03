from fastapi import FastAPI

from app.routers.prediction import router as prediction_router

app = FastAPI(
    title="Oral Cancer Detection API",
    version="1.0.0"
)

app.include_router(prediction_router)


@app.get("/")
def health():
    return {
        "status": "healthy"
    }
