# Oral Cancer Deep Learning Detection System

A web-based deep learning system for early oral cancer detection using ResNet50 image classification with severity assessment, malignancy indicators, and uncertainty estimation.

## Features

- **AI-Powered Detection**: ResNet50 model with 92.67% accuracy
- **Severity Assessment**: Classifies lesions as mild, moderate, or severe
- **Malignancy Screening**: Indicates potentially malignant lesions
- **Uncertainty Quantification**: Test-Time Augmentation (TTA) for reliable confidence scores
- **Heatmap Visualization**: Grad-CAM explainability showing model attention regions
- **PDF Reports**: Automated clinical report generation
- **User Authentication**: Secure login and registration
- **Prediction History**: Track and review past analyses

## Quick Start

### Prerequisites

- Docker and Docker Compose installed

### Deploy

```bash
docker-compose up --build
```

Access the application:
- **Frontend**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs

### Architecture

```
Frontend (React + Tailwind)
    ↓
API (FastAPI)
    ↓
Database (PostgreSQL) + ML Model (ResNet50)
```

## Project Structure

```
.
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py            # Application entry point
│   │   ├── ml/
│   │   │   ├── model.py       # Model loading
│   │   │   ├── inference.py   # TTA inference
│   │   │   ├── explainability.py  # Grad-CAM generation
│   │   │   └── weights/       # Trained model weights
│   │   ├── routers/           # API endpoints
│   │   ├── services/          # Business logic
│   │   └── models/            # Database schemas
│   ├── alembic/               # Database migrations
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                   # React + TypeScript frontend
│   ├── src/
│   │   ├── pages/             # Main pages (Predict, Result, History, etc.)
│   │   ├── components/        # Reusable UI components
│   │   ├── api/               # API client
│   │   └── hooks/             # Custom React hooks
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml         # Multi-container orchestration
├── backend/BACKEND_API.md     # API documentation
└── frontend/README.md         # Frontend setup guide
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | User login |
| POST | `/predict` | Upload image and get prediction |
| GET | `/predictions` | List user's prediction history |
| GET | `/predictions/{id}` | Get prediction details |
| GET | `/reports/{id}` | Download PDF report |
| GET | `/health` | Health check |

See `backend/BACKEND_API.md` for detailed API documentation.

## Database Schema

- **User**: Email, full name, password hash
- **Prediction**: Image, prediction (cancer/non-cancer), confidence, severity, malignancy indicator, heatmap, metadata
- **Report**: Associated PDF report for each prediction

## Environment Variables

### Backend (.env)
```
SECRET_KEY=your-secret-key
ENVIRONMENT=production
DATABASE_URL=postgresql+psycopg://...
AUTO_CREATE_TABLES=true
MAX_FILE_SIZE_MB=10
```

### Frontend (.env)
```
VITE_API_BASE_URL=http://localhost:8000
VITE_USE_MOCKS=false
```

## Model Details

- **Architecture**: ResNet50 pretrained on ImageNet
- **Training Data**: Oral cancer lesion images
- **Classes**: Cancer, Non-Cancer
- **Accuracy**: 92.67%
- **Inference Method**: Test-Time Augmentation (TTA) for uncertainty estimation
- **Output**: Prediction, confidence score, severity level, malignancy indicator

## Deployment

Docker Compose manages three services:
1. **PostgreSQL Database**: Port 5433 (or configured port)
2. **FastAPI Backend**: Port 8000
3. **Nginx Frontend**: Port 3000

All services are containerized and auto-scale with the compose file.

## Troubleshooting

### Database Connection Issues
Ensure PostgreSQL is healthy:
```bash
docker-compose logs db
```

### Model Loading Issues
Check that model weights exist in `backend/app/ml/weights/` or set `MODEL_DOWNLOAD_URL` environment variable.

### Frontend API Connection Issues
Verify `VITE_API_BASE_URL` matches the actual backend URL.

## Support

For API documentation, visit http://localhost:8000/docs (Swagger UI).
For additional information, see `backend/BACKEND_API.md` and `frontend/README.md`.

---

**Status**: Production Ready | **Last Updated**: October 2026
