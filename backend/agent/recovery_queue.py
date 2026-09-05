# RecoverIQ Recovery Queue
#
# Processes the complete payment dataset,
# predicts recovery probability,
# calculates expected value,
# applies agent decisions,
# and creates a ranked recovery queue.

from pathlib import Path

import pandas as pd

from engine import make_decision


# --------------------------------------------------
# Find dataset
# --------------------------------------------------

DATA_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "payments.csv"
)


# --------------------------------------------------
# Load payments
# --------------------------------------------------

df = pd.read_csv(DATA_PATH)

print()
print("RecoverIQ Recovery Queue")
print("========================")
print(f"Payments loaded: {len(df)}")


# --------------------------------------------------
# Process every payment
# --------------------------------------------------

decisions = []

for _, row in df.iterrows():

    event = {
        "event_id": row["event_id"],
        "amount": float(row["amount"]),
        "failure_code": row["failure_code"],

        "customer_tenure_months": int(
            row["customer_tenure_months"]
        ),

        "past_successful_payments": int(
            row["past_successful_payments"]
        ),

        "past_failed_payments": int(
            row["past_failed_payments"]
        ),

        "checkout_funnel_depth": int(
            row["checkout_funnel_depth"]
        ),

        "time_since_failure": float(
            row["time_since_failure"]
        ),

        # These are not currently stored in the dataset,
        # so we use the safe initial values.
        "retry_count": 0,
        "hours_since_contact": None,
    }

    decision = make_decision(event)

    decisions.append(decision)


# --------------------------------------------------
# Convert decisions to DataFrame
# --------------------------------------------------

queue_df = pd.DataFrame(decisions)


# --------------------------------------------------
# Rank by expected value
# --------------------------------------------------

queue_df = queue_df.sort_values(
    by="expected_value",
    ascending=False,
).reset_index(drop=True)


# Add ranking number

queue_df.insert(
    0,
    "rank",
    range(1, len(queue_df) + 1),
)


# --------------------------------------------------
# Save queue
# --------------------------------------------------

OUTPUT_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "recovery_queue.csv"
)

queue_df.to_csv(
    OUTPUT_PATH,
    index=False,
)


# --------------------------------------------------
# Display top 10
# --------------------------------------------------

print()
print("Top 10 Recovery Opportunities")
print("-----------------------------")

display_columns = [
    "rank",
    "event_id",
    "amount",
    "cause",
    "recovery_probability",
    "expected_value",
    "final_action",
]

print(
    queue_df[display_columns]
    .head(10)
    .to_string(index=False)
)


# --------------------------------------------------
# Summary
# --------------------------------------------------

print()
print("Queue Summary")
print("-------------")

print(
    f"Total payments: {len(queue_df)}"
)

print(
    f"Total failed amount: "
    f"₹{queue_df['amount'].sum():,.2f}"
)

print(
    f"Total expected recovered value: "
    f"₹{queue_df['expected_value'].sum():,.2f}"
)

print()
print(f"Queue saved to: {OUTPUT_PATH}")