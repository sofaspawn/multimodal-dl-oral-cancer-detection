# Oral Cancer Detection System - Updated Project Handoff

> **Purpose:** This document is the updated handoff for the current state of the project after the backend and frontend were made operational for demo use. It explains what is already working, what architectural decisions were made, what remains temporary, and what the next agent or developer must accomplish to reach the real final goal: a production-grade AI-assisted oral cancer detection platform.

---

# 1. Project Status Summary

The project is now in a **working demo-ready state**.

This means:

- Frontend is operational
- Backend is operational
- Frontend and backend are integrated
- Authentication flow works
- Image upload flow works
- Prediction history flow works
- Result page flow works
- The system currently supports a **placeholder / pending inference workflow**

Important:

The project is **not yet complete**.

The current system demonstrates:

```text
Register / Login
↓
Upload image
↓
Store image in backend
↓
Create prediction record
↓
Show pending result state
↓
View prediction history
```

It does **not yet perform real ML inference**.

---

# 2. What Was Changed

## 2.1 Frontend

The frontend is now configured to work against the real backend instead of mocks.

### Current frontend state

- React + TypeScript application is present and functional
- Frontend environment configured to use backend API
- Authentication pages exist and work against backend
- Upload flow exists and works against backend
- Result page correctly handles pending inference state
- History page can work with backend prediction history endpoint
- Frontend API client structure is already clean and reusable

### Important frontend integration behavior

The frontend expects these endpoints:

```http
POST /register
POST /login
GET /me
POST /predict
GET /predictions
GET /predictions/{id}
GET /reports/{id}
```

These endpoints are now supported by the backend in demo form.

### Important frontend design assumption

The frontend supports a richer future prediction object:

- prediction label
- confidence score
- heatmap URL
- PDF report URL
- pending inference state
- image URL

Right now, for live backend predictions, the system intentionally returns a **pending inference state** when no model output exists.

That behavior is correct and should be preserved until real inference is integrated.

---

## 2.2 Backend

The backend was refactored from a simple upload endpoint into a layered FastAPI application with working demo endpoints.

### Current backend architecture

```text
Router
↓
Service
↓
In-memory model/store layer
↓
Response schema
```

### Backend layers currently present

#### Core

`backend/app/core/`

- `config.py`
- `security.py`

Purpose:
- application settings
- upload settings
- token generation / verification
- demo password hashing utilities

#### Services

`backend/app/services/`

- `prediction_service.py`

Purpose:
- store uploaded image
- validate file extension
- enforce clean separation from router logic

#### Schemas

`backend/app/schemas/`

- `prediction.py`

Purpose:
- request / response models
- auth schemas
- prediction response schemas

#### Models / Store

`backend/app/models/`

- `store.py`

Purpose:
- in-memory demo persistence for:
  - users
  - predictions

Important:
This is **temporary demo infrastructure**, not production persistence.

#### Routers

`backend/app/routers/`

- `auth.py`
- `prediction.py`

Purpose:
- thin HTTP layer only
- delegate business logic
- enforce auth checks
- expose frontend-compatible endpoints

---

# 3. Current Working Backend Endpoints

## Health

```http
GET /
```

Response:

```json
{
  "status": "healthy"
}
```

---

## Authentication

### Register

```http
POST /register
```

Response:

```json
{
  "access_token": "...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "Test User",
    "created_at": "2026-08-18T18:45:54.167223"
  }
}
```

### Login

```http
POST /login
```

### Current User

```http
GET /me
Authorization: Bearer <token>
```

---

## Predictions

### Upload / Create Prediction

```http
POST /predict
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

Current behavior:
- validates extension
- stores image locally
- creates prediction record
- returns upload success response
- prediction remains pending

Response:

```json
{
  "filename": "cff56c85-4a7d-4ad7-ac61-b2d1768b890c.jpg",
  "status": "uploaded",
  "message": "Image uploaded successfully. Prediction pending ML integration."
}
```

### Prediction History

```http
GET /predictions
Authorization: Bearer <token>
```

Response example:

```json
[
  {
    "prediction_id": 1,
    "prediction": "Pending",
    "confidence": 0.0,
    "created_at": "2026-08-18T18:45:54.470788"
  }
]
```

### Prediction Detail

```http
GET /predictions/{id}
Authorization: Bearer <token>
```

Response example:

```json
{
  "prediction_id": 1,
  "prediction": "Pending",
  "confidence": 0.0,
  "heatmap_url": null,
  "pdf_url": null,
  "filename": "64f684ff-1540-4b01-bab3-7fdb77f53345.jpg",
  "created_at": "2026-08-18T18:46:54.122223",
  "image_url": "/uploads/64f684ff-1540-4b01-bab3-7fdb77f53345.jpg",
  "is_pending_inference": true
}
```

### Report Endpoint

```http
GET /reports/{id}
Authorization: Bearer <token>
```

Current behavior:
- returns error for pending predictions
- PDF generation not implemented yet

---

# 4. Current Directory Snapshot

## Backend

```text
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── security.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── store.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── prediction.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── prediction.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── prediction_service.py
│   └── uploads/
└── requirements.txt
```

## Frontend

```text
frontend/
├── .env
├── package.json
├── vite.config.ts
└── src/
    ├── api/
    ├── components/
    ├── context/
    ├── hooks/
    ├── lib/
    └── pages/
```

---

# 5. Temporary / Demo-Only Decisions

The following are **intentional temporary choices** made to get the demo operational quickly.

## 5.1 In-memory persistence

Users and predictions are currently stored in Python memory.

This means:
- restarting the backend clears data
- no true persistence
- not production-safe
- not multi-instance safe

This must be replaced with PostgreSQL.

---

## 5.2 Simplified auth implementation

Current auth uses lightweight token signing for demo purposes.

This is enough for local/demo functionality but is **not production-ready**.

Needs replacement with:
- proper JWT implementation
- secure password hashing (bcrypt / passlib)
- secret key from environment
- token expiry / refresh strategy

---

## 5.3 No ML inference yet

Current prediction flow does not:
- preprocess image
- load trained model
- run inference
- compute confidence from actual model logits
- generate explainability heatmap
- save generated artifacts

The pending state is currently correct behavior.

---

## 5.4 No PDF generation

Report endpoint is placeholder only.

No PDF report is currently generated or stored.

---

## 5.5 Local file storage only

Images are stored locally under uploads.

For real deployment this needs review:
- persistent disk vs object storage
- file naming policy
- cleanup strategy
- access control

---

# 6. Problems Already Solved

The following integration issues were resolved during this phase:

## Solved

- frontend/backend route mismatch
- auth endpoints missing in backend
- prediction history endpoint missing
- prediction detail endpoint missing
- report endpoint placeholder added
- router/service layering introduced
- upload logic moved out of router
- uploads directory handling fixed
- frontend pending inference state supported correctly
- CORS configured for local frontend/backend integration
- static upload serving enabled so uploaded images can be displayed
- `.gitignore` updated to ignore `__pycache__`

---

# 7. Remaining Gaps Between Demo and Final Goal

The project is still far from the actual final objective.

## Final objective

Build a production-grade AI-assisted oral cancer detection platform that supports:

- authentication
- image upload
- real inference
- confidence score
- explainability heatmap
- prediction history
- downloadable report
- client-ready deployment

## Biggest missing pieces

1. persistent database
2. real authentication/security
3. ML pipeline
4. explainability pipeline
5. report generation
6. deployment hardening
7. clinical/data validation strategy

---

# 8. Immediate Next Objectives for the Next Agent

The next agent should **not** waste time revisiting the demo wiring. That is already done.

The next agent should focus on building the real system in the right order.

## Objective 1 — Replace demo persistence with PostgreSQL

### Required outcome

Move from in-memory stores to real database-backed persistence.

### Tasks

- create database layer
- add SQLAlchemy models or equivalent ORM layer
- create `users`, `predictions`, `reports` tables
- add migrations (Alembic)
- replace `app/models/store.py`
- keep existing API contract stable

### Important note

Do not break the frontend API while replacing persistence.

---

## Objective 2 — Replace demo auth with production-ready auth

### Required outcome

Make authentication real and secure.

### Tasks

- move secrets to environment variables
- use proper JWT library
- use bcrypt/passlib for password hashing
- formalize auth dependency utilities
- optionally introduce refresh tokens later

### Important note

Keep endpoint contract unchanged:

```http
POST /register
POST /login
GET /me
```

---

## Objective 3 — Prepare ML training and inference pipeline

### Required outcome

Make the model a pluggable service that can be integrated without rewriting API routes.

### Tasks

- create `app/ml/` module
- define model loading interface
- define preprocessing pipeline
- define inference result schema
- make `PredictionService` call ML layer
- return actual:
  - prediction
  - confidence
  - heatmap path

### Important note

Do not place ML code directly in routers.

---

## Objective 4 — Integrate explainability (Grad-CAM)

### Required outcome

Generate explainability artifacts for every real prediction.

### Tasks

- implement Grad-CAM pipeline
- save heatmap image
- expose heatmap URL
- ensure frontend result page can display it

---

## Objective 5 — Implement PDF report generation

### Required outcome

Support downloadable report output required by the client.

### Suggested report contents

- patient / case identifier (if available)
- uploaded image preview
- prediction label
- confidence score
- heatmap
- timestamp
- disclaimer

### Tasks

- choose PDF generation approach
- save PDF path in reports table
- implement working `GET /reports/{id}`

---

## Objective 6 — Validate data assumptions with client dataset

### Required outcome

Clarify the real data and inference contract.

### Questions that must be resolved

- Are clinical and histopathology images guaranteed to be paired?
- Will inference use only clinical images or both?
- Is patient metadata available?
- Does metadata affect inference or only reporting?

### Why this matters

This directly affects:
- upload API shape
- frontend upload form
- ML architecture
- database schema

---

# 9. Recommended Technical Roadmap From Here

The next agent should proceed in this order:

## Phase A — Backend foundation hardening

1. environment-based configuration
2. PostgreSQL integration
3. ORM models
4. Alembic migrations
5. production auth

## Phase B — ML integration

1. training notebook to reproducible training script
2. saved model artifact strategy
3. inference service abstraction
4. model loading lifecycle
5. inference endpoint integration

## Phase C — Explainability and reporting

1. Grad-CAM generation
2. heatmap storage
3. PDF generation
4. report endpoint finalization

## Phase D — Deployment hardening

1. Dockerize backend
2. persistent storage strategy
3. cloud deployment
4. frontend production env config
5. security review

---

# 10. Design Constraints the Next Agent Must Respect

The next agent should preserve the following principles:

## Must preserve

- thin routers
- service-layer architecture
- replaceable ML component
- frontend/backend API compatibility
- no business logic in routes
- clean schema-driven responses

## Must avoid

- turning backend into a notebook-style monolith
- putting inference code directly in FastAPI route handlers
- breaking the already working demo flow
- tightly coupling frontend to temporary backend internals

---

# 11. Practical Advice for the Next Agent

If you are the next agent taking over, here is the fastest correct mindset:

## Do not start by rewriting everything.

The current app is already useful as a working scaffold.

## Instead:

1. keep the demo flow intact
2. replace one layer at a time
3. preserve endpoint contracts
4. add persistence first
5. then add real auth
6. then add ML inference
7. then add explainability/reporting

This project already crossed the “frontend/backend integration is broken” phase.

The real work now is turning a demo scaffold into a production-grade clinical research platform.

---

# 12. Short Current State for Quick Transfer

If another agent only needs the short version:

```text
Frontend and backend are now integrated and working.

Current working features:
- register
- login
- get current user
- upload image
- create prediction record
- view prediction history
- view prediction detail
- pending inference state

Current limitations:
- in-memory persistence only
- demo auth only
- no PostgreSQL
- no real ML inference
- no Grad-CAM
- no PDF report

Immediate next real milestone:
Replace demo stores/auth with production-grade persistence and security,
then integrate actual model inference through the service layer.
```

---

# 13. Final Goal Reminder

The final goal is **not** just to classify an image.

The final goal is to deliver a **client-ready research web platform** for oral cancer detection with:

- secure user accounts
- reproducible prediction workflow
- explainable outputs
- report generation
- history and traceability
- deployable architecture

The current system is the operational scaffold for that final product.
