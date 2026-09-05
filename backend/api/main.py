from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException

app = FastAPI(
    title="RecoverIQ API",
    description="Autonomous Revenue Recovery Agent",
    version="1.0.0",
)


# Find the recovery queue
QUEUE_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "recovery_queue.csv"
)


@app.get("/")
def root():
    return {
        "name": "RecoverIQ",
        "status": "running",
        "message": "Autonomous Revenue Recovery Agent API",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/queue")
def get_queue():
    df = pd.read_csv(QUEUE_PATH)

    # Replace NaN values so they can be returned as JSON
    df = df.fillna("")

    return {
        "total_payments": len(df),
        "queue": df.to_dict(orient="records"),
    }

@app.get("/decision/{event_id}")
def get_decision(event_id: str):
    df = pd.read_csv(QUEUE_PATH)

    # Find the requested payment
    matching_rows = df[df["event_id"] == event_id]

    # Payment does not exist
    if matching_rows.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Payment {event_id} not found",
        )

    payment = matching_rows.iloc[0]

    amount = float(payment["amount"])
    recovery_probability = float(payment["recovery_probability"])
    expected_recovered_amount = float(
        payment["expected_recovered_amount"]
    )
    intervention_cost = float(payment["intervention_cost"])
    expected_value = float(payment["expected_value"])

    return {
        "event_id": event_id,
        "amount": amount,
        "failure_code": payment["failure_code"],
        "cause": payment["cause"],
        "strategy": payment["strategy"],
        "recovery_probability": recovery_probability,
        "expected_recovered_amount": expected_recovered_amount,
        "intervention_cost": intervention_cost,
        "expected_value": expected_value,
        "initial_action": payment["initial_action"],
        "final_action": payment["final_action"],
        "safe_to_execute": bool(payment["safe_to_execute"]),
        "rules_triggered": payment["rules_triggered"],
        "reasoning": {
            "formula": "Expected Value = P(recover) × amount − intervention cost",
            "calculation": (
                f"{recovery_probability:.4f} × "
                f"₹{amount:.2f} − "
                f"₹{intervention_cost:.2f}"
            ),
            "result": f"₹{expected_value:.2f}",
        },
    }