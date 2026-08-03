from fastapi import FastAPI

app = FastAPI(
    title="multimodal oral cancer detection API",
    version="1.0.0"
)

@app.get("/")
def health():
    return {
        "status": "healthy",
        "message": "Backend is running"
    }
