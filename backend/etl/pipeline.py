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

print(f"Rows before sampling: {len(df)}")
print(f"Fraud cases before sampling: {df['isfraud'].sum()}")

# To minimize dataset size, keep all fraud rows and keep only a random sample of non-fraud rows per step
fraud = df[df['isfraud'] == 1]
non_fraud = df[df['isfraud'] == 0]

non_fraud_sampled = non_fraud.groupby('step', group_keys=False).apply(
    lambda x: x.sample(frac=0.0774, random_state=42)
)

df = pd.concat([fraud, non_fraud_sampled]).reset_index(drop=True)

print(f"Rows after sampling: {len(df)}")
print(f"Fraud cases after sampling: {df['isfraud'].sum()}")
print(f"Columns: {df.columns.tolist()}")

# Load
print("Loading data...")
engine = create_engine(os.getenv('DATABASE_URL'))
df.to_sql('transactions', engine, if_exists='replace', index=False, chunksize=10000)

print("Done!")