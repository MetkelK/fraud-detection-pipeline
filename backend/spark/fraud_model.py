from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler, StringIndexer
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml.tuning import ParamGridBuilder, CrossValidator
from pyspark.ml import Pipeline
from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

spark = SparkSession.builder \
    .appName("Fraud Detection Model") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

# Load data
print("Loading data...")
csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/PS_20174392719_1491204439457_log.csv'))
df = spark.read.csv(csv_path, header=True, inferSchema=True)

# Drop columns not useful for ML
df = df.drop('nameOrig', 'nameDest', 'isFlaggedFraud')

# Encode transaction type
indexer = StringIndexer(inputCol='type', outputCol='typeIndex')

# Assemble features
assembler = VectorAssembler(
    inputCols=['step', 'amount', 'oldbalanceOrg', 'newbalanceOrig',
               'oldbalanceDest', 'newbalanceDest', 'typeIndex'],
    outputCol='features'
)

# Train/test split
train, test = df.randomSplit([0.8, 0.2], seed=42)
print(f"Train rows: {train.count()}, Test rows: {test.count()}")

# Random Forest
rf = RandomForestClassifier(
    labelCol='isFraud',
    featuresCol='features',
    seed=42
)

# Pipeline
pipeline = Pipeline(stages=[indexer, assembler, rf])

# Parameter grid - test different numTrees values
paramGrid = ParamGridBuilder() \
    .addGrid(rf.numTrees, [50, 100, 200]) \
    .addGrid(rf.maxDepth, [5, 10]) \
    .build()

# Cross validator - 3 folds
evaluator = BinaryClassificationEvaluator(labelCol='isFraud')

cv = CrossValidator(
    estimator=pipeline,
    estimatorParamMaps=paramGrid,
    evaluator=evaluator,
    numFolds=3,
    seed=42
)

# Train with cross validation
print("Training with cross-validation (this will take a while)...")
cv_model = cv.fit(train)

# Best model results
print(f"\nBest AUC: {max(cv_model.avgMetrics):.4f}")
print(f"All AUC scores: {[round(m, 4) for m in cv_model.avgMetrics]}")

# Evaluate best model on test set
predictions = cv_model.transform(test)
test_auc = evaluator.evaluate(predictions)
print(f"Test AUC: {test_auc:.4f}")

# Feature importances from best model
best_rf = cv_model.bestModel.stages[-1]
print("\nFeature importances:")
feature_names = ['step', 'amount', 'oldbalanceOrg', 'newbalanceOrig',
                 'oldbalanceDest', 'newbalanceDest', 'typeIndex']
for name, importance in zip(feature_names, best_rf.featureImportances):
    print(f"  {name}: {importance:.4f}")

# Save the model
model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../model'))
cv_model.bestModel.save(model_path)
print(f"Model saved to {model_path}")