# RecoverIQ Dataset Methodology

## 1. Overview

RecoverIQ uses a synthetic dataset representing failed or at-risk payment events.

The dataset is generated programmatically so that the complete data-generation process is reproducible.

The generator uses a fixed random seed of `42`.

The current dataset contains 10,000 payment events.

The generated dataset is saved as:

`backend/data/payments.csv`

---

## 2. Dataset Fields

Each payment event contains the following fields:

| Field | Description |
|---|---|
| `event_id` | Unique identifier for the payment event |
| `amount` | Payment amount in Indian Rupees |
| `failure_code` | Reason the payment failed or was abandoned |
| `customer_tenure_months` | Number of months the customer has been with the merchant |
| `past_successful_payments` | Number of previous successful payments |
| `past_failed_payments` | Number of previous failed payments |
| `checkout_funnel_depth` | How far the customer progressed through checkout |
| `time_since_failure` | Hours since the payment failure |
| `label_recovered` | Ground-truth recovery outcome: `1` = recovered, `0` = not recovered |

---

## 3. Failure Causes

The dataset contains six failure categories:

1. `insufficient_funds`
2. `gateway_timeout`
3. `checkout_abandon`
4. `mandate_expired`
5. `card_expired`
6. `other`

The generator samples these categories using the following probabilities:

| Failure cause | Sampling probability |
|---|---:|
| insufficient_funds | 25% |
| gateway_timeout | 20% |
| checkout_abandon | 18% |
| mandate_expired | 12% |
| card_expired | 12% |
| other | 13% |

These are sampling probabilities, not recovery probabilities.

---

## 4. Payment Amount

Payment amounts are generated using a log-normal distribution.

This gives the dataset a realistic shape where:

- many payments are relatively small
- some payments are substantially larger

The generated values are constrained between:

- Minimum: ₹100
- Maximum: ₹100,000

Values are rounded to two decimal places.

---

## 5. Customer History

Customer tenure is generated between 1 and 60 months.

Previous successful payments are generated using a Poisson distribution with a mean of approximately 8.

Previous failed payments are generated using a Poisson distribution with a mean of approximately 2.

These features provide the recovery model with information about the customer's historical payment behaviour.

---

## 6. Checkout Funnel Depth

Checkout funnel depth ranges from 1 to 5.

Higher values represent customers who progressed further through the checkout process.

This feature is only meaningful for:

`checkout_abandon`

For other failure causes, the value is set to `0`.

---

## 7. Time Since Failure

Time since failure is generated in hours using an exponential distribution.

Values are constrained between:

- 0.1 hours
- 72 hours

This allows the dataset to contain both very recent failures and older failures.

---

## 8. Ground-Truth Recovery Generation

The `label_recovered` field is not assigned using a simple fixed rule such as:

`probability > 50% = recovered`

Instead, the generator first calculates an underlying recovery probability.

This probability depends on several factors:

- failure cause
- customer payment history
- customer tenure
- time since failure
- checkout funnel depth

A logistic transformation converts the combined effects into a probability between 0 and 1.

The final recovery outcome is then sampled using that probability.

For example, if an event has an underlying recovery probability of 0.80, it has an 80% chance of receiving:

`label_recovered = 1`

and a 20% chance of receiving:

`label_recovered = 0`

This introduces realistic variation between individual payment events.

---

## 9. Cause-Specific Recovery Signals

The synthetic generation process intentionally gives different failure causes different recovery signals.

### Gateway timeout

Gateway timeout events receive a strong positive recovery signal.

They also become less favourable as more time passes after the failure.

This represents a scenario where an immediate retry can often recover a transient gateway failure.

### Insufficient funds

Insufficient-funds events receive a moderate recovery signal.

The generator also includes a timing effect around approximately 24 hours after failure.

This represents the possibility that a later retry can succeed after the customer's available balance changes.

### Checkout abandonment

Checkout abandonment receives a negative baseline signal.

However, deeper checkout progression increases the recovery probability.

The idea is that a customer who reached a later stage of checkout may have stronger purchase intent than someone who abandoned immediately.

### Mandate expired

Mandate-expired events receive a lower baseline recovery signal.

Recovery may require customer intervention or re-authorization.

### Card expired

Card-expired events receive a strong negative signal because retrying the same expired card is unlikely to succeed without a payment-method update.

### Other

The `other` category has the lowest baseline recovery signal because the failure reason is not known to represent a specific recoverable condition.

---

## 10. Reproducibility

The generator uses:

`SEED = 42`

Therefore, running the generator again with the same code and seed produces the same synthetic dataset.

This allows the model-training and evaluation process to be reproduced.

---

## 11. Important Evaluation Rule

The generated dataset is not used as a single dataset for both training and evaluation.

It will later be divided into:

- 80% training data
- 20% held-out evaluation data

The recovery model will only be evaluated on the held-out portion.

Precision, recall, ROC-AUC, and calibration results shown by RecoverIQ will be calculated from this held-out evaluation set.

No model performance number will be manually entered or fabricated.

---

## 12. Why Synthetic Data?

This project uses synthetic data because real payment data contains sensitive financial and customer information.

The synthetic generator allows us to demonstrate the complete revenue-recovery workflow without exposing real customer payment information.

The generation rules are explicitly documented so that the dataset can be inspected and reproduced.