import numpy as np
import pandas as pd
from pathlib import Path


# ============================================================
# RECOVERIQ - SYNTHETIC PAYMENT DATASET GENERATOR
# ============================================================

# Fixed seed = same dataset every time we run the program.
SEED = 42

# Number of payment events we want.
N_RECORDS = 10000

# Create our random number generator.
rng = np.random.default_rng(SEED)


# ============================================================
# 1. EVENT ID
# ============================================================

event_id = [
    f"PAY_{i:05d}"
    for i in range(1, N_RECORDS + 1)
]


# ============================================================
# 2. PAYMENT AMOUNT
# ============================================================

# Real payment amounts are not all the same.
# Most payments are relatively small,
# while some payments are much larger.

amount = rng.lognormal(
    mean=np.log(2500),
    sigma=1.0,
    size=N_RECORDS
)

# Keep amounts between ₹100 and ₹1,00,000.
amount = np.clip(amount, 100, 100000)

# Round to two decimal places.
amount = np.round(amount, 2)


# ============================================================
# 3. FAILURE CODE
# ============================================================

failure_codes = [
    "insufficient_funds",
    "gateway_timeout",
    "checkout_abandon",
    "mandate_expired",
    "card_expired",
    "other"
]

failure_code = rng.choice(
    failure_codes,
    size=N_RECORDS,
    p=[
        0.25,  # insufficient funds
        0.20,  # gateway timeout
        0.18,  # checkout abandonment
        0.12,  # mandate expired
        0.12,  # card expired
        0.13   # other
    ]
)


# ============================================================
# 4. CUSTOMER TENURE
# ============================================================

# How many months the customer has been with the merchant.

customer_tenure_months = rng.integers(
    1,
    61,
    size=N_RECORDS
)


# ============================================================
# 5. PAST SUCCESSFUL PAYMENTS
# ============================================================

past_successful_payments = rng.poisson(
    lam=8,
    size=N_RECORDS
)


# ============================================================
# 6. PAST FAILED PAYMENTS
# ============================================================

past_failed_payments = rng.poisson(
    lam=2,
    size=N_RECORDS
)


# ============================================================
# 7. CHECKOUT FUNNEL DEPTH
# ============================================================

# Possible values:
#
# 1 = barely started
# 2 = early stage
# 3 = middle
# 4 = near payment
# 5 = reached payment stage
#
# This feature matters primarily for checkout abandonment.

checkout_funnel_depth = rng.integers(
    1,
    6,
    size=N_RECORDS
)

# For payments that did NOT fail because of checkout abandonment,
# we set this value to 0 because it isn't relevant.

checkout_funnel_depth = np.where(
    failure_code == "checkout_abandon",
    checkout_funnel_depth,
    0
)


# ============================================================
# 8. TIME SINCE FAILURE
# ============================================================

# Number of hours since the payment failed.

time_since_failure = rng.exponential(
    scale=12,
    size=N_RECORDS
)

# Keep values between 0.1 and 72 hours.

time_since_failure = np.clip(
    time_since_failure,
    0.1,
    72
)

time_since_failure = np.round(
    time_since_failure,
    2
)


# ============================================================
# 9. CREATE UNDERLYING RECOVERY PROBABILITY
# ============================================================

# IMPORTANT:
#
# We are NOT simply saying:
#
# gateway_timeout = 85%
#
# Instead, recovery probability depends on:
#
# - failure cause
# - customer history
# - timing
# - checkout behaviour
#
# This underlying probability is used ONLY to generate
# our synthetic ground truth.
#
# The ML model will later have to LEARN these patterns.


# Start with zero effect.
logit = np.zeros(N_RECORDS)


# ------------------------------------------------------------
# Failure cause effect
# ------------------------------------------------------------

logit += np.where(
    failure_code == "gateway_timeout",
    1.00,
    0
)

logit += np.where(
    failure_code == "insufficient_funds",
    0.10,
    0
)

logit += np.where(
    failure_code == "checkout_abandon",
    -1.10,
    0
)

logit += np.where(
    failure_code == "mandate_expired",
    -0.20,
    0
)

logit += np.where(
    failure_code == "card_expired",
    -1.70,
    0
)

logit += np.where(
    failure_code == "other",
    -2.10,
    0
)


# ------------------------------------------------------------
# Customer history
# ------------------------------------------------------------

# More successful historical payments slightly increase
# the chance of recovery.

logit += (
    0.035
    * (past_successful_payments - 8)
)


# More historical failures slightly decrease
# the chance of recovery.

logit -= (
    0.08
    * (past_failed_payments - 2)
)


# Longer customer tenure provides a small positive signal.

logit += (
    0.015
    * (customer_tenure_months - 30)
)


# ------------------------------------------------------------
# Gateway timeout timing
# ------------------------------------------------------------

# A gateway timeout is more recoverable when the retry
# happens relatively soon after the failure.

gateway_timing_effect = np.where(
    failure_code == "gateway_timeout",
    np.exp(-time_since_failure / 12),
    0
)

logit += (
    0.8
    * gateway_timing_effect
)


# ------------------------------------------------------------
# Insufficient funds timing
# ------------------------------------------------------------

# Insufficient-funds failures may become more recoverable
# after some time has passed.

insufficient_delay_effect = np.where(
    failure_code == "insufficient_funds",
    np.exp(
        -(
            (time_since_failure - 24) ** 2
        )
        /
        (2 * 18 ** 2)
    ),
    0
)

logit += (
    0.6
    * insufficient_delay_effect
)


# ------------------------------------------------------------
# Checkout abandonment
# ------------------------------------------------------------

# Deeper funnel = stronger purchase intent.

logit += np.where(
    failure_code == "checkout_abandon",
    0.30 * checkout_funnel_depth,
    0
)


# ============================================================
# 10. CONVERT LOGIT → PROBABILITY
# ============================================================

recovery_probability = (
    1 /
    (
        1 +
        np.exp(-logit)
    )
)


# Keep probabilities away from exactly 0 or 1.

recovery_probability = np.clip(
    recovery_probability,
    0.01,
    0.99
)


# ============================================================
# 11. GENERATE GROUND-TRUTH OUTCOME
# ============================================================

# IMPORTANT:
#
# We don't simply set:
#
# probability > 50% → recovered
#
# Instead we randomly generate the outcome according
# to the probability.
#
# Example:
#
# P(recovery) = 0.80
#
# means approximately 80% of similar events recover,
# not that every individual event recovers.

label_recovered = (
    rng.random(N_RECORDS)
    < recovery_probability
).astype(int)


# ============================================================
# 12. CREATE DATAFRAME
# ============================================================

df = pd.DataFrame({

    "event_id": event_id,

    "amount": amount,

    "failure_code": failure_code,

    "customer_tenure_months":
        customer_tenure_months,

    "past_successful_payments":
        past_successful_payments,

    "past_failed_payments":
        past_failed_payments,

    "checkout_funnel_depth":
        checkout_funnel_depth,

    "time_since_failure":
        time_since_failure,

    "label_recovered":
        label_recovered
})


# ============================================================
# 13. SAVE DATASET
# ============================================================

# Find the backend/data folder.

output_directory = (
    Path(__file__).resolve().parent.parent / "data"
)

# Create the folder if it doesn't exist.

output_directory.mkdir(
    parents=True,
    exist_ok=True
)


# Name of our CSV file.

output_file = (
    output_directory / "payments.csv"
)


# Save CSV.

df.to_csv(
    output_file,
    index=False
)


# ============================================================
# 14. DISPLAY RESULTS
# ============================================================

print()
print("=" * 60)
print("RECOVERIQ DATASET GENERATED")
print("=" * 60)

print()
print(f"Total records: {len(df)}")

print()
print(f"Dataset saved to:")
print(output_file)

print()
print("-" * 60)
print("FAILURE DISTRIBUTION")
print("-" * 60)

print(
    df["failure_code"].value_counts()
)


print()
print("-" * 60)
print("OVERALL RECOVERY RATE")
print("-" * 60)

print(
    f"{df['label_recovered'].mean():.2%}"
)


print()
print("-" * 60)
print("RECOVERY RATE BY FAILURE CAUSE")
print("-" * 60)

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
print("DONE")
print("=" * 60)