import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Extract
print("Extracting data...")
df = pd.read_csv('../../data/PS_20174392719_1491204439457_log.csv')

# Transform
print("Transforming data...")

# Lowercase column names
df.columns = df.columns.str.lower()

# Drop columns not useful for ML
df = df.drop(columns=['nameorig', 'namedest', 'isflaggedfraud'])

# Add feature: flag suspicious transaction types
df['is_suspicious_type'] = df['type'].isin(['TRANSFER', 'CASH_OUT']).astype(int)

# One-hot encode transaction type
df = pd.get_dummies(df, columns=['type'])

print(f"Rows: {len(df)}")
print(f"Columns: {df.columns.tolist()}")
print(f"Fraud cases: {df['isfraud'].sum()}")

# Load
print("Loading data...")
engine = create_engine(os.getenv('DATABASE_URL'))
df.to_sql('transactions', engine, if_exists='replace', index=False, chunksize=10000)

print("Done!")