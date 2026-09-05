# RecoverIQ Safety Rules
# Prevents unsafe, repeated, or low-confidence recovery actions.


MAX_RETRIES = 3
CONTACT_COOLDOWN_HOURS = 24
LOW_CONFIDENCE_THRESHOLD = 0.10


def check_safety(
    retry_count: int,
    hours_since_contact: float | None,
    recovery_probability: float,
    expected_value: float,
    intervention_cost: float,
) -> dict:
    """
    Apply RecoverIQ stopping rules.

    Returns:
        {
            "safe": bool,
            "action": str,
            "rules_triggered": list[str]
        }
    """

    rules_triggered = []

    # Rule 1: Maximum retry limit
    if retry_count >= MAX_RETRIES:
        rules_triggered.append(
            "Maximum retry limit reached"
        )

        return {
            "safe": False,
            "action": "escalate_to_human",
            "rules_triggered": rules_triggered,
        }

    # Rule 2: Customer contact cooldown
    if (
        hours_since_contact is not None
        and hours_since_contact < CONTACT_COOLDOWN_HOURS
    ):
        rules_triggered.append(
            "Customer contacted within the last 24 hours"
        )

        return {
            "safe": False,
            "action": "no_action",
            "rules_triggered": rules_triggered,
        }

    # Rule 3: Low-confidence / ambiguous prediction
    if abs(recovery_probability - 0.5) <= LOW_CONFIDENCE_THRESHOLD:
        rules_triggered.append(
            "Recovery probability is ambiguous"
        )

        return {
            "safe": False,
            "action": "escalate_to_human",
            "rules_triggered": rules_triggered,
        }

    # Rule 4: Intervention costs more than expected value
    if expected_value <= intervention_cost:
        rules_triggered.append(
            "Expected value does not justify intervention cost"
        )

        return {
            "safe": False,
            "action": "no_action",
            "rules_triggered": rules_triggered,
        }

    # No safety rule was triggered
    rules_triggered.append(
        "All safety checks passed"
    )

    return {
        "safe": True,
        "action": None,
        "rules_triggered": rules_triggered,
    }


if __name__ == "__main__":

    print("RecoverIQ Safety Rules")
    print("----------------------")

    # Test 1: Safe payment
    result = check_safety(
        retry_count=0,
        hours_since_contact=None,
        recovery_probability=0.75,
        expected_value=3748,
        intervention_cost=2,
    )

    print("\nTest 1 - Safe:")
    print(result)

    # Test 2: Retry limit reached
    result = check_safety(
        retry_count=3,
        hours_since_contact=None,
        recovery_probability=0.75,
        expected_value=3748,
        intervention_cost=2,
    )

    print("\nTest 2 - Retry limit:")
    print(result)

    # Test 3: Recent customer contact
    result = check_safety(
        retry_count=0,
        hours_since_contact=5,
        recovery_probability=0.75,
        expected_value=3748,
        intervention_cost=2,
    )

    print("\nTest 3 - Recent contact:")
    print(result)

    # Test 4: Ambiguous probability
    result = check_safety(
        retry_count=0,
        hours_since_contact=None,
        recovery_probability=0.52,
        expected_value=2598,
        intervention_cost=2,
    )

    print("\nTest 4 - Low confidence:")
    print(result)