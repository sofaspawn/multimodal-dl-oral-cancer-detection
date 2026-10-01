# Graph Report - oral-cancer-deep-learning  (2026-10-02)

## Corpus Check
- 88 files · ~50,631 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 12 file(s) not represented in the graph (top: (none) 6, .example 2, .ini 1)

## Summary
- 689 nodes · 1332 edges · 39 communities (27 shown, 12 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 24 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `125642de`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- ResultPage.tsx
- types.ts
- routers/auth.py
- Deployment Checklist
- Oral Cancer Deep Learning - Implementation Summary
- ✅ DEPLOYMENT READY
- index.ts
- ✅ Implementation Complete
- routers/prediction.py
- BACKEND_API.md
- compilerOptions
- inference.py
- train_model
- package.json
- compilerOptions
- Enhanced Model Training Summary
- security.py
- train_enhanced.py
- evaluate_model.py
- PredictionService
- upload_prediction
- devDependencies
- ConfidenceGauge.tsx
- db.py
- ImageDropzone.tsx
- explainability.py
- dependencies
- scripts
- vite.config.ts
- Settings
- React + TypeScript + Vite
- env.d.ts
- tsconfig.json
- CLAUDE.md

## God Nodes (most connected - your core abstractions)
1. `cn()` - 26 edges
2. `Button()` - 23 edges
3. `react` - 20 edges
4. `compilerOptions` - 20 edges
5. `PredictionService` - 16 edges
6. `compilerOptions` - 15 edges
7. `predict_image()` - 13 edges
8. `Prediction` - 13 edges
9. `react-router-dom` - 13 edges
10. `ApiError` - 13 edges

## Surprising Connections (you probably didn't know these)
- `Files Modified` --references--> `SeverityLevel`  [INFERRED]
  IMPLEMENTATION_SUMMARY.md → frontend/src/api/types.ts
- `upload_prediction()` --uses--> `PredictionUploadResponse`  [INFERRED]
  backend/app/routers/prediction.py → backend/app/schemas/prediction.py
- `upload_prediction()` --uses--> `PredictionService`  [INFERRED]
  backend/app/routers/prediction.py → backend/app/services/prediction_service.py
- `list_predictions()` --uses--> `PredictionService`  [INFERRED]
  backend/app/routers/prediction.py → backend/app/services/prediction_service.py
- `get_prediction()` --uses--> `PredictionService`  [INFERRED]
  backend/app/routers/prediction.py → backend/app/services/prediction_service.py

## Import Cycles
- None detected.

## Communities (39 total, 12 thin omitted)

### Community 0 - "ResultPage.tsx"
Cohesion: 0.05
Nodes (74): listPredictions(), PatientMetadata, App(), AppShell(), DisclaimerBanner(), FullPageSpinner(), ProtectedRoute(), PublicOnlyRoute() (+66 more)

### Community 1 - "types.ts"
Cohesion: 0.12
Nodes (34): login(), logout(), me(), register(), clearToken(), ErrorPayload, extractDetail(), getJson() (+26 more)

### Community 2 - "routers/auth.py"
Cohesion: 0.12
Nodes (13): create_access_token(), hash_password(), verify_password(), login(), me(), register(), AuthResponse, LoginRequest (+5 more)

### Community 3 - "Deployment Checklist"
Cohesion: 0.06
Nodes (33): 1. Backend Deployment, 1. Database Migration ⚠️ REQUIRED, 1. Test Backend, 2. Frontend Deployment, 2. Test Frontend, 2. Verify Enhanced Model is Present, 3. Code Compilation Check ✅, 3. Test History Page (+25 more)

### Community 4 - "Oral Cancer Deep Learning - Implementation Summary"
Cohesion: 0.06
Nodes (33): Assessment Logic, Augmentations Used, Backend, Changes Made, Database Migration, Documentation, Enhanced Model, Enhanced Training (+25 more)

### Community 5 - "✅ DEPLOYMENT READY"
Cohesion: 0.07
Nodes (29): API Response Format (Example), Backend ✅, Code Comments, Database ✅, Database Changes, Database Status: ✅ COMPLETE, Deployment Instructions, ✅ DEPLOYMENT READY (+21 more)

### Community 6 - "index.ts"
Cohesion: 0.14
Nodes (26): ApiError, addRecord(), allRecords(), findRecord(), hashString(), hoursAgo(), mockHeatmap(), mockInference() (+18 more)

### Community 7 - "✅ Implementation Complete"
Cohesion: 0.07
Nodes (27): 1. Database Migration (REQUIRED), 2. Deploy Backend, 3. Deploy Frontend, 4. Verify Deployment, All Requirements Successfully Implemented, Backend (7 files), Code Quality, Database (1 file) (+19 more)

### Community 8 - "routers/prediction.py"
Cohesion: 0.17
Nodes (3): Report, User, ReportService

### Community 9 - "BACKEND_API.md"
Cohesion: 0.08
Nodes (23): Authentication, Base URL, Content-Type, Current Backend Features, Current Project Structure, Current Response, Endpoint, Endpoint (+15 more)

### Community 10 - "compilerOptions"
Cohesion: 0.09
Nodes (21): compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection (+13 more)

### Community 11 - "inference.py"
Cohesion: 0.14
Nodes (7): _assess_potentially_malignant(), _calculate_entropy(), _determine_severity(), _get_tta_transforms(), predict_image(), predict_image_legacy(), PredictionResult

### Community 12 - "train_model"
Cohesion: 0.12
Nodes (7): EarlyStopping, FocalLoss, get_resnet50_with_dropout(), LabelSmoothingCrossEntropy, mixup_criterion(), mixup_data(), train_model()

### Community 13 - "package.json"
Cohesion: 0.13
Nodes (17): name, private, type, version, clsx, eslint, @eslint/js, eslint-plugin-react-hooks (+9 more)

### Community 14 - "compilerOptions"
Cohesion: 0.12
Nodes (16): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, noEmit, noFallthroughCasesInSwitch (+8 more)

### Community 15 - "Enhanced Model Training Summary"
Cohesion: 0.12
Nodes (15): Early-Stage Lesion Detection (Requirement 4), Enhanced Model Training Summary, Evaluate Model, False Positive Reduction, Improved Malignancy Assessment, Inference Improvements (Requirement 3 & 4), Model Location, Next Steps for Further Improvement (+7 more)

### Community 16 - "security.py"
Cohesion: 0.17
Nodes (4): decode_token(), TokenPayload, get_db(), get_current_user()

### Community 18 - "evaluate_model.py"
Cohesion: 0.19
Nodes (6): load_model(), analyze_calibration(), evaluate_on_dataset(), main(), plot_calibration_curve(), test_random_images()

### Community 20 - "upload_prediction"
Cohesion: 0.18
Nodes (8): download_report(), get_prediction(), list_predictions(), _record_to_detail(), _record_to_history_item(), upload_prediction(), PredictionDetail, PredictionHistoryItem

### Community 21 - "devDependencies"
Cohesion: 0.13
Nodes (15): devDependencies, eslint, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh, globals, tailwindcss, @tailwindcss/vite (+7 more)

### Community 22 - "ConfidenceGauge.tsx"
Cohesion: 0.23
Nodes (12): SeverityLevel, COLOURS, ConfidenceGauge(), getSnapshot(), subscribe(), usePrefersReducedMotion(), confidenceBand, formatPercent() (+4 more)

### Community 23 - "db.py"
Cohesion: 0.19
Nodes (4): Base, health(), health_check(), lifespan()

### Community 24 - "ImageDropzone.tsx"
Cohesion: 0.27
Nodes (11): ImageDropzone(), handleDrop(), handleInputChange(), select(), setPreview(), ImageDropzoneProps, ACCEPT_ATTRIBUTE, ALLOWED_EXTENSIONS (+3 more)

### Community 27 - "dependencies"
Cohesion: 0.25
Nodes (8): dependencies, clsx, @hookform/resolvers, react, react-dom, react-hook-form, react-router-dom, zod

### Community 28 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, preview

### Community 29 - "vite.config.ts"
Cohesion: 0.40
Nodes (3): @tailwindcss/vite, vite, @vitejs/plugin-react

### Community 31 - "React + TypeScript + Vite"
Cohesion: 0.50
Nodes (3): Expanding the ESLint configuration, React Compiler, React + TypeScript + Vite

## Knowledge Gaps
- **230 isolated node(s):** `name`, `private`, `version`, `type`, `dev` (+225 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 327 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SeverityLevel` connect `ConfidenceGauge.tsx` to `types.ts`, `index.ts`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Why does `Oral Cancer Deep Learning - Implementation Summary` connect `Oral Cancer Deep Learning - Implementation Summary` to `ConfidenceGauge.tsx`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `PredictionService` (e.g. with `download_report()` and `get_prediction()`) actually correct?**
  _`PredictionService` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `name`, `private`, `version` to the rest of the system?**
  _230 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `ResultPage.tsx` be split into smaller, more focused modules?**
  _Cohesion score 0.054840416152354084 - nodes in this community are weakly interconnected._
- **Should `types.ts` be split into smaller, more focused modules?**
  _Cohesion score 0.11962833914053426 - nodes in this community are weakly interconnected._
- **Should `routers/auth.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11586452762923351 - nodes in this community are weakly interconnected._