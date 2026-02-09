# AI-Powered Network Security Detection

## Overview
This project provides an end-to-end ML pipeline for phishing network activity detection. It ingests records from MongoDB, validates and transforms data, trains classification models, and exports artifacts for serving. A FastAPI app can trigger training and run predictions from the latest `final_model/` artifacts. The system can optionally sync artifacts to S3 and track experiments with MLflow (via DagsHub). CI/CD builds and pushes the container to ECR and deploys it on a self-hosted runner.


## Components
### Data Layer
- **MongoDB** - Primary source for phishing network records. Credentials are stored in environment variables and used by `networksecurity.components.data_ingestion`.
- **Data Seeder (`push_data.py`)** - Loads `Network_Data/phisingData.csv` and inserts records into MongoDB for training.
- **Feature Store (CSV on disk)** - Intermediate storage in `Artifacts/<timestamp>/data_ingestion/feature_store/` to preserve raw exports per run.

### Machine Learning Pipeline
- **Training Orchestration (`TrainingPipeline`)** - Coordinates ingestion, validation, transformation, and training; optionally syncs artifacts to S3.
- **Data Ingestion** - Pulls data from MongoDB, materializes CSV copies, and splits into train/test sets.
- **Data Validation** - Validates column count using `data_schema/schema.yaml` and generates a KS-test drift report.
- **Data Transformation** - Applies a `KNNImputer`, creates NumPy arrays, and exports the preprocessing object.
- **Model Trainer** - Trains multiple classifiers, selects the best model, tracks metrics with MLflow, and saves model artifacts.
- **Artifact Versioning** - Each run uses timestamped directories under `Artifacts/`.

### Model & Artifact Management
- **Local `Artifacts/`** - Stores per-run outputs such as train/test splits, drift reports, transformed arrays, and trained models.
- **Local `final_model/`** - Holds the currently deployed `preprocessor.pkl` and `model.pkl` for FastAPI inference.
- **AWS S3 (Optional)** - Centralized storage for artifacts (`artifact/<timestamp>/`) and final models (`final_model/<timestamp>/`).
- **MLflow + DagsHub** - Tracks experiment metrics and model artifacts.

### Serving Layer
- **FastAPI Application (`app.py`)** - Exposes REST endpoints:
- `GET /train` to trigger the training pipeline.
- `POST /predict` to accept a CSV upload, run inference, and return HTML results while saving `prediction_output/output.csv`.
- **NetworkModel Wrapper** - Combines preprocessor and model to standardize prediction logic.

### Infrastructure & Deployment
- **Docker** - Containerizes the FastAPI app with dependencies from `requirements.txt`.
- **GitHub Actions** - Builds and pushes the container image to ECR on `main` pushes, then deploys from a self-hosted runner.
- **Amazon ECR** - Stores built images.
- **Self-hosted Runner/EC2** - Pulls and runs the container with AWS credentials injected as environment variables.
- **S3 Sync (`S3Sync`)** - After training, artifacts and final models can be synchronized to S3.

### Observability & Operations
- **Logging** - Python logging streams to timestamped log files under `logs/`.
- **Monitoring** - MLflow metrics and drift reports support model-performance monitoring.

## Data & Control Flow
1. **Training Trigger** - Manually via `main.py`, `app.py` (`/train`), or an automated scheduler.
2. **Data Ingestion** - Pulls fresh data from MongoDB into the feature store and splits datasets.
3. **Validation & Transformation** - Ensures schema compliance, handles drift, and prepares model-ready tensors.
4. **Model Training** - Trains, evaluates, and persists the model and preprocessing pipeline locally.
5. **Artifact Sync** - Uploads artifacts and final model directories to S3. Logs and metrics are captured in MLflow.
6. **Model Serving** - FastAPI loads the latest `final_model/` contents for inference. Predictions are exported to `prediction_output/output.csv` and rendered as HTML.

## Deployment Topology
- **Development** - Run the pipeline locally using Python (or Docker).
- **CI/CD** - GitHub Actions builds and pushes the container to ECR and deploys via a self-hosted runner.
- **Production** - A self-hosted runner or EC2 instance pulls the image from ECR and runs the FastAPI service.

## Security & Compliance Considerations
- Store secrets (MongoDB URI, AWS credentials) in a secure secret manager (AWS Secrets Manager, GitHub Secrets, or environment variables injected at runtime).
- Restrict network access to MongoDB and S3 via IAM roles and security groups.
- Enable encryption at rest (S3 SSE, MongoDB encryption) and in transit (TLS).
- Implement IAM roles for EC2 instances to remove long-lived AWS keys on hosts.

## Repo Layout (Key Paths)
- `app.py` - FastAPI serving layer.
- `main.py` - Local training entrypoint.
- `networksecurity/` - Pipeline code, components, utilities, and configs.
- `data_schema/schema.yaml` - Schema for validation and drift checks.
- `Artifacts/` - Per-run outputs and metadata.
- `final_model/` - Latest model and preprocessor for inference.
- `prediction_output/` - Saved prediction results.
- `.github/workflows/main.yaml` - CI/CD pipeline definition.

## Notes and Known Gaps
- The serving app uses `MONGODB_URL_KEY` while the pipeline uses `MONGO_DB_URL`. Consolidate to a single environment variable name.
- CloudWatch is not wired in code; add explicit handlers if centralized logging is needed.

## Setup GitHub Secrets
- `AWS_ACCESS_KEY_ID=`
- `AWS_SECRET_ACCESS_KEY=`
- `AWS_REGION=us-east-1`
- `AWS_ECR_LOGIN_URI=788614365622.dkr.ecr.us-east-1.amazonaws.com/networkssecurity`
- `ECR_REPOSITORY_NAME=networkssecurity`

## Docker Setup In EC2
Optional
- `sudo apt-get update -y`
- `sudo apt-get upgrade`

Required
- `curl -fsSL https://get.docker.com -o get-docker.sh`
- `sudo sh get-docker.sh`
- `sudo usermod -aG docker ubuntu`
- `newgrp docker`
