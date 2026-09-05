# RecoverIQ Decision Engine
# Complete pipeline:
# Diagnosis -> ML Probability -> Expected Value -> Action -> Safety

from pathlib import Path

import joblib
import pandas as pd

from diagnosis import diagnose
from ranker import rank_payment
from actions import choose_action
from safety import check_safety


# --------------------------------------------------
# Load trained RecoverIQ model
# --------------------------------------------------

MODEL_PATH = (
    Path(__file__).resolve().parent.parent
    / "models"
    / "recoveriq_model.joblib"
)

model = joblib.load(MODEL_PATH)


# --------------------------------------------------
# Predict recovery probability
# --------------------------------------------------

def predict_recovery_probability(event: dict) -> float:

    features = pd.DataFrame(
        [
            {
                "amount": event["amount"],
                "failure_code": event["failure_code"],
                "customer_tenure_months": event[
                    "customer_tenure_months"
                ],
                "past_successful_payments": event[
                    "past_successful_payments"
                ],
                "past_failed_payments": event[
                    "past_failed_payments"
                ],
                "checkout_funnel_depth": event[
                    "checkout_funnel_depth"
                ],
                "time_since_failure": event[
                    "time_since_failure"
                ],
            }
        ]
    )

    probability = model.predict_proba(features)[0][1]

    return round(float(probability), 4)


# --------------------------------------------------
# Complete RecoverIQ decision
# --------------------------------------------------

def make_decision(event: dict) -> dict:

    # 1. Diagnose failure
    diagnosis = diagnose(
        event["failure_code"]
    )

    # 2. Get real ML probability
    recovery_probability = (
        predict_recovery_probability(event)
    )

    # 3. Choose cause-aware action
    action = choose_action(
        event["failure_code"]
    )

    # 4. Calculate expected value
    ranking = rank_payment(
        amount=event["amount"],
        recovery_probability=recovery_probability,
        action=action,
    )

    # 5. Apply safety rules
    safety = check_safety(
        retry_count=event.get("retry_count", 0),
        hours_since_contact=event.get(
            "hours_since_contact"
        ),
        recovery_probability=recovery_probability,
        expected_value=ranking["expected_value"],
        intervention_cost=ranking["intervention_cost"],
    )

    # 6. Determine final action
    final_action = action

    if not safety["safe"]:
        final_action = safety["action"]

    # 7. Return complete decision
    return {
        "event_id": event["event_id"],
        "amount": event["amount"],
        "failure_code": event["failure_code"],
        "cause": diagnosis["cause"],
        "strategy": diagnosis["strategy"],
        "recovery_probability": recovery_probability,
        "expected_recovered_amount": ranking[
            "expected_recovered_amount"
        ],
        "intervention_cost": ranking[
            "intervention_cost"
        ],
        "expected_value": ranking[
            "expected_value"
        ],
        "initial_action": action,
        "final_action": final_action,
        "safe_to_execute": safety["safe"],
        "rules_triggered": safety[
            "rules_triggered"
        ],
    }


# --------------------------------------------------
# Test the complete engine
# --------------------------------------------------

if __name__ == "__main__":

    test_event = {
        "event_id": "demo_001",
        "amount": 5000,
        "failure_code": "gateway_timeout",

        "customer_tenure_months": 24,
        "past_successful_payments": 18,
        "past_failed_payments": 2,
        "checkout_funnel_depth": 4,
        "time_since_failure": 2,

        "retry_count": 0,
        "hours_since_contact": None,
    }

    result = make_decision(test_event)

    print()
    print("RecoverIQ Decision")
    print("==================")

    for key, value in result.items():
        print(f"{key}: {value}")