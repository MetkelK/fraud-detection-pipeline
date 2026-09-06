from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from pyspark.sql import SparkSession
from pyspark.ml import PipelineModel
from dotenv import load_dotenv
import psycopg2
import os

load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))
model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../model'))

app = FastAPI(title="Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

def get_db():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

@app.get("/")
def root():
    return {"message": "Detection API is running"}

@app.get("/stats")
def get_stats():
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) FROM transactions")
    total = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM transactions WHERE isfraud = 1")
    fraud_count = cur.fetchone()[0]
    
    cur.execute("SELECT SUM(amount) FROM transactions WHERE isfraud = 1")
    fraud_amount = cur.fetchone()[0]
    
    cur.close()
    conn.close()
    
    return {
        "total_transactions": total,
        "fraud_count": fraud_count,
        "fraud_rate": round(fraud_count / total * 100, 4),
        "total_fraud_amount": round(fraud_amount, 2)
    }

@app.get("/fraud-by-type")
def get_fraud_by_type():
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            CASE 
                WHEN "type_CASH_OUT" = true THEN 'CASH_OUT'
                WHEN "type_TRANSFER" = true THEN 'TRANSFER'
                WHEN "type_PAYMENT" = true THEN 'PAYMENT'
                WHEN "type_CASH_IN" = true THEN 'CASH_IN'
                WHEN "type_DEBIT" = true THEN 'DEBIT'
            END AS transaction_type,
            COUNT(*) AS total,
            SUM(isfraud::int) AS fraud_count,
            ROUND(SUM(isfraud::int) * 100.0 / COUNT(*), 4) AS fraud_rate
        FROM transactions
        GROUP BY transaction_type
        ORDER BY fraud_rate DESC
    """)
    
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    return [
        {
            "type": row[0],
            "total": row[1],
            "fraud_count": row[2],
            "fraud_rate": float(row[3])
        }
        for row in rows
    ]

@app.get("/fraud-over-time")
def get_fraud_over_time():
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            step,
            COUNT(*) AS total_transactions,
            SUM(isfraud::int) AS fraud_count
        FROM transactions
        GROUP BY step
        ORDER BY step ASC
    """)
    
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    return [
        {
            "step": row[0],
            "total_transactions": row[1],
            "fraud_count": row[2]
        }
        for row in rows
    ]

@app.get("/model-info")
def get_model_info():
    return {
        "auc": 0.9967,
        "test_auc": 0.9966,
        "best_params": {
            "numTrees": 200,
            "maxDepth": 10
        },
        "train_rows": 5089767,
        "test_rows": 1272853,
        "all_auc_scores": [0.9877, 0.9964, 0.9866, 0.9964, 0.9879, 0.9967],
        "feature_importances": {
            "step": 0.0386,
            "amount": 0.0524,
            "oldbalanceOrg": 0.2721,
            "newbalanceOrig": 0.0533,
            "oldbalanceDest": 0.0759,
            "newbalanceDest": 0.3558,
            "typeIndex": 0.1518
        }
    }

spark = SparkSession.builder \
    .appName("Detection API") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

cv_model = PipelineModel.load(model_path)

class Transaction(BaseModel):
    type: str
    amount: float
    oldbalanceOrg: float
    newbalanceOrig: float
    oldbalanceDest: float
    newbalanceDest: float

    @field_validator('type')
    @classmethod
    def type_must_be_valid(cls, v):
        valid_types = ['CASH_IN', 'CASH_OUT', 'TRANSFER', 'PAYMENT', 'DEBIT']
        if v not in valid_types:
            raise ValueError('Invalid transaction type')
        return v

    @field_validator('amount')
    @classmethod
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v
    
@app.post("/predict")
def predict(transaction: Transaction):
    data = [{
        "step": 1,
        "type": transaction.type,
        "amount": transaction.amount,
        "oldbalanceOrg": transaction.oldbalanceOrg,
        "newbalanceOrig": transaction.newbalanceOrig,
        "oldbalanceDest": transaction.oldbalanceDest,
        "newbalanceDest": transaction.newbalanceDest,
        "isFraud": 0
    }]

    df = spark.createDataFrame(data)
    prediction = cv_model.transform(df)
    
    result = prediction.select("prediction", "probability").first()
    probability = float(result["probability"][1])
    is_fraud = bool(result["prediction"] == 1.0)

    return {
        "is_fraud": is_fraud,
        "probability": round(probability, 4),
        "risk_level": "HIGH" if probability > 0.7 else "MEDIUM" if probability > 0.3 else "LOW"
    }