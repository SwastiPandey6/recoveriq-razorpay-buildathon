# RecoverIQ Expected Value Ranker
# Calculates the economic value of attempting to recover a payment.


# Estimated intervention costs in INR.
# These represent the operational cost assigned to each action.
INTERVENTION_COSTS = {
    "retry_now": 2.0,
    "retry_scheduled": 2.0,
    "send_payment_link": 1.0,
    "escalate_to_human": 25.0,
    "no_action": 0.0,
}


def calculate_expected_value(
    amount: float,
    recovery_probability: float,
    action: str,
) -> float:
    """
    Calculate the expected recovered value after intervention cost.

    Formula:
        EV = P(recover) × amount − intervention cost
    """

    intervention_cost = INTERVENTION_COSTS.get(action, 0.0)

    expected_value = (
        recovery_probability * amount
    ) - intervention_cost

    return round(expected_value, 2)


def rank_payment(
    amount: float,
    recovery_probability: float,
    action: str,
) -> dict:
    """
    Calculate expected value and return the ranking information.
    """

    intervention_cost = INTERVENTION_COSTS.get(action, 0.0)

    expected_recovered_amount = (
        recovery_probability * amount
    )

    expected_value = calculate_expected_value(
        amount,
        recovery_probability,
        action,
    )

    return {
        "amount": amount,
        "recovery_probability": recovery_probability,
        "action": action,
        "intervention_cost": intervention_cost,
        "expected_recovered_amount": round(
            expected_recovered_amount,
            2,
        ),
        "expected_value": expected_value,
    }


if __name__ == "__main__":
    # Simple local test
    result = rank_payment(
        amount=5000,
        recovery_probability=0.70,
        action="retry_now",
    )

    print("Expected Value calculation")
    print("--------------------------")
    print(result)