![phData Logo](phData.png "phData Logo")

``# Sound Realty House Price Prediction API

A production-ready REST API for predicting house prices in the Seattle area using machine learning. Features zero-downtime deployment strategies including rolling updates and blue-green deployments.

---

## Table of Contents

- [Quick Start](#quick-start)
- [Deployment Options](#deployment-options)
- [API Endpoints](#api-endpoints)
- [Model Versions](#model-versions)
- [Project Structure](#project-structure)
- [Requirements Completed](#requirements-completed)
- [Documentation](#documentation)

---

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Build and start the service
docker-compose up --build

# API available at http://localhost:8080
```

### Option 2: Local Development

**With Conda:**
```bash
conda env create -f conda_environment.yml
conda activate housing
python src/app.py
```

**With venv:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python src/app.py
```

---

## Deployment Options

### Standard Deployment (docker-compose.yml)

Use this for simple, single-version deployments.

**Start the API:**
```bash
docker-compose up -d
```

**Deploy a different model version:**
```bash
# Deploy v2.0
export MODEL_VERSION=2.0
docker-compose up -d --build

# Deploy v1.0
export MODEL_VERSION=1.0
docker-compose up -d --build
```

**Check status:**
```bash
# Health check
curl http://localhost:8080/health

# Model information
curl http://localhost:8080/model/info

# Stop service
docker-compose down
```

**Features:**
- ✅ Simple single-version deployment
- ✅ Rolling updates for zero downtime
- ✅ Health checks
- ✅ Auto-restart on failure

---

### Blue-Green Deployment (docker-compose-bluegreen.yml)

Use this when you want to test a new model version thoroughly before switching production traffic.

**What is Blue-Green?**
- **Blue** = Current production version (v1.0)
- **Green** = New version being tested (v2.0)
- Both run simultaneously on different ports
- Switch traffic instantly when ready
- Instant rollback if issues

**Start Blue-Green deployment:**

```bash
# 1. Start Blue (v1.0) on port 8080
docker-compose -f docker-compose-bluegreen.yml up -d api-blue

# 2. Start Green (v2.0) on port 8081
docker-compose -f docker-compose-bluegreen.yml --profile green up -d api-green

# 3. Start with Nginx load balancer (optional)
docker-compose -f docker-compose-bluegreen.yml --profile loadbalancer up -d
```

**Test both versions:**
```bash
# Test Blue (v1.0)
curl http://localhost:8080/health

# Test Green (v2.0)
curl http://localhost:8081/health

# Test through Nginx (port 80)
curl http://localhost/health
```

**Compare predictions:**
```bash
# Blue prediction
curl -X POST http://localhost:8080/predict/minimal \
  -H "Content-Type: application/json" \
  -d '{
    "bedrooms": 3,
    "bathrooms": 2.5,
    "sqft_living": 2220,
    "sqft_lot": 6380,
    "floors": 1.5,
    "sqft_above": 1660,
    "sqft_basement": 560,
    "zipcode": "98115"
  }'

# Green prediction
curl -X POST http://localhost:8081/predict/minimal \
  -H "Content-Type: application/json" \
  -d '{
    "bedrooms": 3,
    "bathrooms": 2.5,
    "sqft_living": 2220,
    "sqft_lot": 6380,
    "floors": 1.5,
    "sqft_above": 1660,
    "sqft_basement": 560,
    "zipcode": "98115"
  }'
```

**Switch traffic (with Nginx):**

1. Edit `nginx.conf` line 19:
```nginx
upstream api_active {
    server api-green:8080;  # Switch from api-blue to api-green
}
```

2. Reload Nginx:
```bash
docker-compose -f docker-compose-bluegreen.yml restart nginx
```

3. Verify switch:
```bash
curl http://localhost/health
# Should now show v2.0
```

**Instant rollback:**
```bash
# Just switch nginx.conf back to api-blue and restart
docker-compose -f docker-compose-bluegreen.yml restart nginx
```

**Stop Blue-Green:**
```bash
docker-compose -f docker-compose-bluegreen.yml --profile green --profile loadbalancer down
```

**Features:**
- ✅ Test new version in production-like environment
- ✅ Both versions running simultaneously
- ✅ Instant traffic switching
- ✅ Instant rollback capability
- ✅ Zero downtime


---

## API Endpoints

### Health Check
```bash
GET /health

Response:
{
  "status": "healthy",
  "model_loaded": true,
  "model_version": "1.0",
  "model_loaded_at": "2026-03-09T10:30:00.123456"
}
```

### Model Information
```bash
GET /model/info

Response:
{
  "model_version": "1.0",
  "model_directory": "models/v1.0",
  "features_count": 33,
  "features": ["bedrooms", "bathrooms", ...],
  "loaded_at": "2026-03-09T10:30:00.123456",
  "demographics_zipcodes": 70
}
```

### Full Prediction
Accepts all 18 house features. Demographics are added automatically on the backend.

```bash
POST /predict

Request:
{
  "bedrooms": 4,
  "bathrooms": 1.0,
  "sqft_living": 1680,
  "sqft_lot": 5043,
  "floors": 1.5,
  "waterfront": 0,
  "view": 0,
  "condition": 4,
  "grade": 6,
  "sqft_above": 1680,
  "sqft_basement": 0,
  "yr_built": 1911,
  "yr_renovated": 0,
  "zipcode": "98118",
  "lat": 47.5354,
  "long": -122.273,
  "sqft_living15": 1560,
  "sqft_lot15": 5765
}

Response:
{
  "prediction": 450000.0,
  "model_version": "1.0",
  "features_used": [...],
  "timestamp": "2026-03-09T10:30:00.123456"
}
```

### Minimal Prediction (Bonus Endpoint)
Accepts only the 8 required features.

```bash
POST /predict/minimal

Request:
{
  "bedrooms": 4,
  "bathrooms": 1.0,
  "sqft_living": 1680,
  "sqft_lot": 5043,
  "floors": 1.5,
  "sqft_above": 1680,
  "sqft_basement": 0,
  "zipcode": "98118"
}

Response:
{
  "prediction": 450000.0,
  "model_version": "1.0",
  "minimal_features_used": [...],
  "timestamp": "2026-03-09T10:30:00.123456"
}
```

---

## Model Versions

Models are organized in the `models/` directory:

```
models/
├── v1.0/
│   ├── model.pkl              # KNN model
│   └── model_features.json    # Feature list
└── v2.0/
    ├── model.pkl              # Random Forest model
    └── model_features.json    # Feature list
```

### Switching Between Versions

**Standard deployment:**
```bash
# Deploy v1.0
export MODEL_VERSION=1.0
docker-compose up -d --build

# Deploy v2.0
export MODEL_VERSION=2.0
docker-compose up -d --build
```

**Blue-Green deployment:**
- Blue always runs v1.0 (port 8080)
- Green always runs v2.0 (port 8081)
- Switch traffic via Nginx configuration

### Adding New Versions

```bash
# 1. Create new version directory
mkdir -p models/v3.0

# 2. Train and save model
python scripts/create_model.py
mv model/model.pkl models/v3.0/
mv model/model_features.json models/v3.0/

# 3. Deploy
export MODEL_VERSION=3.0
docker-compose up -d --build
```

---


## Testing

### Run Test Suite

```bash
# Start API
docker-compose up -d

# Run tests
python tests/test_api.py
python tests/example_request.py
```

### Test Model Versions

```bash
# Test v1.0
./scripts/test_model_version.sh 1.0

# Test v2.0
./scripts/test_model_version.sh 2.0
```


## License

This project is for interview purposes.

---

**Built with ❤️ for phData Machine Learning Engineer Interview**
