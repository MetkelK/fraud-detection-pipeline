# Fraud Detection Pipeline

A full-stack, cloud-deployed fraud detection system: a PySpark ML model served through a FastAPI backend, a React dashboard frontend, and a CI/CD pipeline that deploys both to AWS on every push.

**Live demo:** https://d1cduluh0dxamx.cloudfront.net

## What it does

Trains a Random Forest classifier (PySpark MLlib, AUC 0.9967) on the PaySim synthetic financial transactions dataset (~6.3M rows) to detect fraudulent transactions in real time. The API serves live predictions plus dashboard analytics (fraud rate, fraud by transaction type, fraud over time) backed by a Postgres database.

## Architecture

```
┌───────────────────┐         ┌────────────────────────────────────────────┐
│  React frontend   │  HTTPS  │              AWS EC2 (t4g.small)           │
│  (S3 + CloudFront)├────────►│  Docker container: FastAPI + PySpark model │
└───────────────────┘         │  (fronted by a second CloudFront distro)   │
                              └───────────────────┬────────────────────────┘
                                                  │
                                                  ▼
                                         Supabase (Postgres)
```

- **Frontend:** React + Vite + Recharts, built and deployed to S3, served over HTTPS via CloudFront
- **Backend:** FastAPI + PySpark (Java 21), containerized with Docker, running on an ARM (Graviton) EC2 instance, fronted by a second CloudFront distribution for HTTPS
- **Database:** Supabase-managed Postgres, Row Level Security enabled, sampled dataset (~500K rows, preserving class balance) to fit free-tier storage limits
- **CI/CD:** GitHub Actions — builds and pushes the Docker image to Docker Hub, deploys to EC2 via AWS Systems Manager (no exposed SSH), builds and syncs the frontend to S3, and invalidates the CloudFront cache — all on push to `main`
- **Monitoring:** CloudWatch alarms for instance health and disk usage
- **Security:** rate limiting (`slowapi`) on all endpoints, SSH access closed entirely (SSM Session Manager only), scoped IAM permissions per credential, RLS on the database

## Tech stack

| Layer    | Tools                                                 |
| -------- | ----------------------------------------------------- |
| ML       | PySpark MLlib, Random Forest                          |
| Backend  | FastAPI, Python, psycopg2                             |
| Frontend | React, Vite, Recharts, TanStack Query, axios          |
| Database | Postgres (Supabase)                                   |
| Infra    | Docker, AWS EC2, S3, CloudFront, IAM, SSM, CloudWatch |
| CI/CD    | GitHub Actions                                        |

## API endpoints

Interactive API docs available at `/docs` on the backend (FastAPI's built-in Swagger UI).

- `POST /predict` — real-time fraud prediction for a transaction
- `GET /stats` — summary statistics (total transactions, fraud count/rate)
- `GET /fraud-by-type` — fraud breakdown by transaction type
- `GET /fraud-over-time` — fraud counts across the time series
- `GET /model-info` — model performance metrics and feature importances

## Running locally

**Backend:**

```bash
cd backend
pip install -r requirements.txt
uvicorn api.main:app --reload
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

Requires a `.env` file with `DATABASE_URL` pointing to a Postgres instance, and the trained model present in `/model`.

## Notable engineering decisions

- **EC2 over Lambda:** the model's PySpark/JVM dependency has significant cold-start overhead — a poor fit for Lambda's on-demand execution model. EC2 keeps the Spark session warm.
- **CloudFront over an Application Load Balancer:** needed HTTPS termination for a single origin with no load-balancing requirement; CloudFront provides this within AWS's free tier, whereas an ALB has a flat hourly cost regardless of usage.
- **SSM Session Manager over SSH:** all remote access and CI/CD deploys go through AWS Systems Manager, so port 22 is closed entirely — no direct internet-facing SSH exposure.
- **Sampled dataset with class balance preserved:** the full PaySim dataset exceeded Supabase's free-tier storage limit; the serving database uses a ~500K row sample stratified by transaction step, oversampling fraud cases to keep dashboard visualizations representative, while the model itself was trained on the full dataset.
