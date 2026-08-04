"""Smoke test for the refactored backend."""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Health check
print("=== Health Check ===")
r = client.get("/")
print(r.json())

# Valid upload
print("\n=== Upload Valid Image ===")
with open("../app/uploads/thinker.jpg", "rb") as f:
    r = client.post("/predict", files={"file": ("thinker.jpg", f, "image/jpeg")})
print(f"Status: {r.status_code}")
print(r.json())

# Invalid file type
print("\n=== Upload Invalid File ===")
import io
r = client.post("/predict", files={"file": ("test.txt", io.BytesIO(b"hello"), "text/plain")})
print(f"Status: {r.status_code}")
print(r.json())

# No file
print("\n=== No File ===")
r = client.post("/predict")
print(f"Status: {r.status_code}")

print("\n=== All tests passed ===")
