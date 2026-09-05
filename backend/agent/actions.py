# RecoverIQ Action Selector
# Chooses a recovery action based on the diagnosed failure cause.


ALLOWED_ACTIONS = {
    "retry_now",
    "retry_scheduled",
    "send_payment_link",
    "escalate_to_human",
    "no_action",
}


CAUSE_ACTION_MAP = {
    "gateway_timeout": "retry_now",
    "insufficient_funds": "retry_scheduled",
    "checkout_abandon": "send_payment_link",
    "mandate_expired": "send_payment_link",
    "card_expired": "escalate_to_human",
    "other": "escalate_to_human",
}


def choose_action(failure_code: str) -> str:
    """
    Select the safest recovery action for a failure cause.

    Only actions from ALLOWED_ACTIONS can be returned.
    """

    action = CAUSE_ACTION_MAP.get(
        failure_code,
        "escalate_to_human",
    )

    if action not in ALLOWED_ACTIONS:
        return "escalate_to_human"

    return action


if __name__ == "__main__":
    test_codes = [
        "gateway_timeout",
        "insufficient_funds",
        "checkout_abandon",
        "mandate_expired",
        "card_expired",
        "other",
    ]

    print("RecoverIQ Action Selector")
    print("------------------------")

    for code in test_codes:
        action = choose_action(code)
        print(f"{code} -> {action}")