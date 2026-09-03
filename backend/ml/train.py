import pandas as pd

from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    precision_score,
    recall_score,
    roc_auc_score,
)
import numpy as np

import joblib


# Find the dataset
data_path = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "payments.csv"
)

# Load the dataset
df = pd.read_csv(data_path)

print("Dataset loaded successfully!")
print("Rows:", len(df))
print("Columns:", len(df.columns))

# Columns used by the model
feature_columns = [
    "amount",
    "failure_code",
    "customer_tenure_months",
    "past_successful_payments",
    "past_failed_payments",
    "checkout_funnel_depth",
    "time_since_failure",
]

# Input data
X = df[feature_columns]

# Target / answer
y = df["label_recovered"]

print()
print("Features:", X.shape)
print("Target:", y.shape)

# Split the dataset into training and held-out test data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y,
)

print()
print("Training rows:", len(X_train))
print("Held-out test rows:", len(X_test))

# Numerical features
numeric_features = [
    "amount",
    "customer_tenure_months",
    "past_successful_payments",
    "past_failed_payments",
    "checkout_funnel_depth",
    "time_since_failure",
]

# Categorical features
categorical_features = [
    "failure_code",
]

# Preprocess numerical and categorical features separately
preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_features,
        ),
        (
            "numeric",
            StandardScaler(),
            numeric_features,
        ),
    ]
)

# Create the complete machine-learning pipeline
model = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        (
            "classifier",
            LogisticRegression(
                max_iter=1000,
                random_state=42,
            ),
        ),
    ]
)

# Train the model using ONLY the training data
model.fit(X_train, y_train)

print()
print("Model trained successfully!")

# Predict recovery probabilities on the held-out test set
test_probabilities = model.predict_proba(X_test)[:, 1]

print()
print("First 10 predicted recovery probabilities:")
print(test_probabilities[:10])
# Convert probabilities into 0/1 predictions using a 0.50 threshold
test_predictions = (test_probabilities >= 0.50).astype(int)

# Calculate metrics on the held-out test set
precision = precision_score(y_test, test_predictions)
recall = recall_score(y_test, test_predictions)
auc = roc_auc_score(y_test, test_probabilities)

print()
print("Held-out model metrics")
print("----------------------")
print(f"Precision: {precision:.4f}")
print(f"Recall:    {recall:.4f}")
print(f"ROC-AUC:   {auc:.4f}")
# Calibration sanity check
print()
print("Calibration check")
print("-----------------")

bins = np.linspace(0, 1, 6)

for lower, upper in zip(bins[:-1], bins[1:]):
    if upper == 1:
        mask = (test_probabilities >= lower) & (test_probabilities <= upper)
    else:
        mask = (test_probabilities >= lower) & (test_probabilities < upper)

    if mask.sum() > 0:
        predicted_mean = test_probabilities[mask].mean()
        actual_rate = y_test[mask].mean()

        print(
            f"{lower:.1f}-{upper:.1f}: "
            f"predicted={predicted_mean:.3f}, "
            f"actual={actual_rate:.3f}, "
            f"count={mask.sum()}"
        )

        # Save the trained model
model_path = (
    Path(__file__).resolve().parent.parent
    / "models"
    / "recoveriq_model.joblib"
)

joblib.dump(model, model_path)

print()
print("Model saved successfully!")
print(f"Saved to: {model_path}")