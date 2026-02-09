# Project Architecture

## Overview
This document expands the solution architecture with sequence and deployment views aligned to the current code and CI/CD workflow.

## Sequence Diagrams

### Training Trigger (`GET /train`)
```mermaid
sequenceDiagram
    actor User
    participant FastAPI as FastAPI (app.py)
    participant TP as TrainingPipeline
    participant DI as DataIngestion
    participant DV as DataValidation
    participant DT as DataTransformation
    participant MT as ModelTrainer
    participant S3 as S3Sync (Optional)
    participant ML as MLflow/DagsHub

    User->>FastAPI: GET /train
    FastAPI->>TP: run_pipeline()
    TP->>DI: initiate_data_ingestion()
    DI-->>TP: DataIngestionArtifact
    TP->>DV: initiate_data_validation(artifact)
    DV-->>TP: DataValidationArtifact
    TP->>DT: initiate_data_transformation(artifact)
    DT-->>TP: DataTransformationArtifact
    TP->>MT: initiate_model_trainer(artifact)
    MT->>ML: log metrics, log model
    MT-->>TP: ModelTrainerArtifact
    TP->>S3: sync_artifact_dir_to_s3()
    TP->>S3: sync_saved_model_dir_to_s3()
    TP-->>FastAPI: success
    FastAPI-->>User: 200 Training is successful
```

### Prediction (`POST /predict`)
```mermaid
sequenceDiagram
    actor User
    participant FastAPI as FastAPI (app.py)
    participant FS as final_model/
    participant NM as NetworkModel

    User->>FastAPI: POST /predict (CSV file)
    FastAPI->>FS: load preprocessor.pkl
    FastAPI->>FS: load model.pkl
    FastAPI->>NM: predict(dataframe)
    NM-->>FastAPI: predictions
    FastAPI-->>User: HTML table response
```

## Deployment Diagram
```mermaid
flowchart TB
    subgraph Dev[Developer]
        Code[Code Push to main]
    end

    subgraph CI[GitHub Actions]
        Build[Build Docker Image]
        Push[Push to ECR]
    end

    subgraph AWS[AWS]
        ECR[(Amazon ECR)]
        EC2[(Self-hosted Runner/EC2)]
        S3[(S3 Artifact Bucket)]
        Mongo[(MongoDB)]
    end

    subgraph Runtime[FastAPI Runtime]
        App[FastAPI Container]
        Models[final_model/]
    end

    Code --> Build --> Push --> ECR
    EC2 -->|docker pull| ECR
    EC2 -->|docker run| App
    App --> Models
    App -->|/train| Mongo
    App -->|sync (optional)| S3
```

## Key Paths
- `docs/solution_architecture.md` - Detailed system description.
- `app.py` - FastAPI endpoints for training and prediction.
- `networksecurity/pipeline/training_pipeline.py` - Orchestration logic.
- `.github/workflows/main.yaml` - CI/CD pipeline.
