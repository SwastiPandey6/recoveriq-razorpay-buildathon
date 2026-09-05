# RecoverIQ Cause Diagnosis
# Determines the reason for a failed payment and
# maps it to the appropriate recovery strategy.


CAUSE_MAP = {
    "insufficient_funds": {
        "cause": "Insufficient funds",
        "strategy": "Retry after 24 hours",
    },
    "gateway_timeout": {
        "cause": "Gateway timeout",
        "strategy": "Retry immediately",
    },
    "checkout_abandon": {
        "cause": "Checkout abandonment",
        "strategy": "Send payment link",
    },
    "mandate_expired": {
        "cause": "Mandate expired",
        "strategy": "Send re-authorization link",
    },
    "card_expired": {
        "cause": "Card expired",
        "strategy": "Request payment method update",
    },
    "other": {
        "cause": "Other failure",
        "strategy": "Escalate for review",
    },
}


def diagnose(failure_code: str) -> dict:
    """
    Diagnose the cause of a failed payment.

    Returns the cause and recommended recovery strategy.
    """

    result = CAUSE_MAP.get(
        failure_code,
        {
            "cause": "Unknown failure",
            "strategy": "Escalate for review",
        },
    )

    return {
        "failure_code": failure_code,
        "cause": result["cause"],
        "strategy": result["strategy"],
    }


if __name__ == "__main__":
    # Simple local test
    test_codes = [
        "insufficient_funds",
        "gateway_timeout",
        "checkout_abandon",
        "mandate_expired",
        "card_expired",
        "other",
    ]

    for code in test_codes:
        print(diagnose(code))