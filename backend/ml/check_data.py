import pandas as pd
from pathlib import Path


# Find the dataset
data_path = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "payments.csv"
)


# Load dataset
df = pd.read_csv(data_path)


print("=" * 60)
print("RECOVERIQ DATASET CHECK")
print("=" * 60)

print()

# Number of rows and columns
print("Dataset shape:")
print(df.shape)

print()

# Column names
print("Columns:")
print(list(df.columns))

print()

# Missing values
print("Missing values:")
print(df.isnull().sum())

print()

# Duplicate event IDs
print("Duplicate event IDs:")
print(df["event_id"].duplicated().sum())

print()

# Label distribution
print("Recovery labels:")
print(df["label_recovered"].value_counts())

print()

# Recovery rate
print("Overall recovery rate:")
print(
    f"{df['label_recovered'].mean():.2%}"
)

print()

# Failure-code distribution
print("Failure-code distribution:")
print(df["failure_code"].value_counts())

print()

# Recovery by cause
print("Recovery rate by failure cause:")

recovery_by_cause = (
    df.groupby("failure_code")["label_recovered"]
    .mean()
    .sort_values(ascending=False)
)

print(
    recovery_by_cause
    .map(lambda x: f"{x:.2%}")
)

print()

print("=" * 60)
print("DATASET CHECK COMPLETE")
print("=" * 60)