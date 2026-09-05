from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="RecoverIQ API",
    description="Autonomous Revenue Recovery Agent",
    version="1.0.0",
)


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# DATA PATH
# --------------------------------------------------

QUEUE_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "recovery_queue.csv"
)


# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def load_queue():
    if not QUEUE_PATH.exists():
        raise HTTPException(
            status_code=500,
            detail="Recovery queue data file not found",
        )

    return pd.read_csv(QUEUE_PATH)


def parse_bool(value):
    """
    Correctly convert CSV boolean values.
    bool("False") incorrectly returns True,
    so we explicitly parse the string.
    """
    if isinstance(value, bool):
        return value

    return str(value).strip().lower() in {
        "true",
        "1",
        "yes",
        "y",
    }


# --------------------------------------------------
# ROOT
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "name": "RecoverIQ",
        "status": "running",
        "message": "Autonomous Revenue Recovery Agent API",
    }


# --------------------------------------------------
# HEALTH
# --------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# --------------------------------------------------
# RECOVERY QUEUE
# --------------------------------------------------

@app.get("/queue")
def get_queue():

    df = load_queue()

    # Remove NaN values
    df = df.fillna("")

    total_payments = len(df)

    total_failed_amount = (
        pd.to_numeric(
            df["amount"],
            errors="coerce"
        )
        .fillna(0)
        .sum()
    )

    total_expected_recovered_value = (
        pd.to_numeric(
            df["expected_value"],
            errors="coerce"
        )
        .fillna(0)
        .sum()
    )

    return {
        "total_payments": int(total_payments),

        "total_failed_amount": round(
            float(total_failed_amount),
            2
        ),

        "total_expected_recovered_value": round(
            float(total_expected_recovered_value),
            2
        ),

        "queue": df.to_dict(
            orient="records"
        ),
    }


# --------------------------------------------------
# DECISION ENGINE
# --------------------------------------------------

@app.get("/decision/{event_id}")
def get_decision(event_id: str):

    df = load_queue()

    matching_rows = df[
        df["event_id"].astype(str) == str(event_id)
    ]

    if matching_rows.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Payment {event_id} not found",
        )

    payment = matching_rows.iloc[0]

    amount = float(payment["amount"])

    recovery_probability = float(
        payment["recovery_probability"]
    )

    expected_recovered_amount = float(
        payment["expected_recovered_amount"]
    )

    intervention_cost = float(
        payment["intervention_cost"]
    )

    expected_value = float(
        payment["expected_value"]
    )

    return {
        "event_id": event_id,

        "amount": amount,

        "failure_code": str(
            payment["failure_code"]
        ),

        "cause": str(
            payment["cause"]
        ),

        "strategy": str(
            payment["strategy"]
        ),

        "recovery_probability":
            recovery_probability,

        "expected_recovered_amount":
            expected_recovered_amount,

        "intervention_cost":
            intervention_cost,

        "expected_value":
            expected_value,

        "initial_action": str(
            payment["initial_action"]
        ),

        "final_action": str(
            payment["final_action"]
        ),

        "safe_to_execute":
            parse_bool(
                payment["safe_to_execute"]
            ),

        "rules_triggered": str(
            payment["rules_triggered"]
        ),

        "reasoning": {
            "formula":
                "Expected Value = P(recover) × amount − intervention cost",

            "calculation": (
                f"{recovery_probability:.4f} × "
                f"₹{amount:.2f} − "
                f"₹{intervention_cost:.2f}"
            ),

            "result":
                f"₹{expected_value:.2f}",
        },
    }