#!/bin/bash
set -e

cd backend
source .venv/bin/activate

# Start server in background
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
SERVER_PID=$!
sleep 3

echo "=== Health Check ==="
curl -s http://localhost:8000/ | python -m json.tool

echo ""
echo "=== Upload Valid Image ==="
curl -s -X POST http://localhost:8000/predict -F "file=@app/uploads/thinker.jpg" | python -m json.tool

echo ""
echo "=== Upload Invalid File ==="
echo "test" > /tmp/fake.txt
curl -s -X POST http://localhost:8000/predict -F "file=@/tmp/fake.txt" | python -m json.tool

echo ""
echo "=== Done ==="
kill $SERVER_PID 2>/dev/null
