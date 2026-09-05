\# RecoverIQ — Revenue Recovery Intelligence



RecoverIQ is an autonomous revenue recovery agent that identifies failed payments that are economically worth recovering.



Instead of treating every failed payment equally, RecoverIQ combines machine-learning recovery probability, failure diagnosis, expected-value optimization, and safety rules to determine the best recovery action.



\## Live Demo



Frontend:

https://recoveriq-frontned.onrender.com/



Backend API:

https://recoveriq-razorpay-buildathon.onrender.com/



API Documentation:

https://recoveriq-razorpay-buildathon.onrender.com/docs



GitHub:

https://github.com/SwastiPandey6/recoveriq-razorpay-buildathon



\---



\## Problem



Payment failures represent lost revenue, but blindly retrying every failed payment can waste money, annoy customers, and create unnecessary operational load.



The key question is:



> Which failed payment should we try to recover, what action should we take, and is that action economically justified?



RecoverIQ answers this question automatically.



\---



\## Solution



RecoverIQ processes a failed payment through an autonomous decision pipeline:



Payment Failure

&#x20;       ↓

Failure Diagnosis

&#x20;       ↓

Recovery Probability

&#x20;       ↓

Expected Value Calculation

&#x20;       ↓

Action Selection

&#x20;       ↓

Safety Checks

&#x20;       ↓

Final Recovery Action

&#x20;       ↓

Prioritized Recovery Queue



\---



\## Core Features



\### 1. Recovery Probability Model



A machine-learning model predicts the probability that a failed payment can be successfully recovered.



Features include:



\- Payment amount

\- Failure code

\- Customer tenure

\- Previous successful payments

\- Previous failed payments

\- Checkout funnel depth

\- Time since failure



The model uses a preprocessing pipeline with categorical encoding, numerical scaling, and logistic regression.



\### 2. Failure Diagnosis



RecoverIQ maps payment failure codes to understandable causes and recovery strategies.



Examples:



| Failure Code | Cause | Strategy |

|---|---|---|

| gateway\_timeout | Gateway timeout | Retry immediately |

| insufficient\_funds | Insufficient funds | Retry after 24 hours |

| checkout\_abandon | Checkout abandonment | Send payment link |

| mandate\_expired | Mandate expired | Send re-authorization link |

| card\_expired | Card expired | Request payment method update |

| other | Other failure | Escalate for review |



\### 3. Expected-Value Ranking



RecoverIQ does not simply prioritize payments by size or probability.



It calculates:



Expected Value = P(recover) × Amount − Intervention Cost



This allows the system to prioritize actions that have the highest economic value.



\### 4. Action Selection



The agent selects an appropriate intervention:



\- Retry immediately

\- Schedule retry

\- Send payment link

\- Escalate to human



\### 5. Safety Layer



Before an action is executed, RecoverIQ checks safety constraints.



Examples include:



\- Maximum retry limit

\- Recent customer contact

\- Ambiguous recovery probability



Unsafe actions are prevented or escalated.



\### 6. Recovery Queue



The system processes the payment dataset and generates a prioritized recovery queue.



The dashboard displays:



\- Payment rank

\- Payment amount

\- Failure cause

\- Recovery probability

\- Expected value

\- Recommended action



\---



\## Machine Learning Results



The model was evaluated on a held-out test set.



Precision: 0.6673



Recall: 0.7757



ROC-AUC: 0.7818



Calibration was also checked across probability ranges to compare predicted recovery probabilities against observed recovery rates.



\---



\## Example Decision



For a failed payment:



Amount: ₹5,000



Failure: Gateway timeout



Recovery probability: approximately 94%



Expected recovered amount: approximately ₹4,700



Intervention cost: ₹2



Expected value: approximately ₹4,698



Final action:



Retry Now



Safety status:



Safe to execute



\---



\## Technology Stack



\### Backend



\- Python

\- FastAPI

\- Pandas

\- Scikit-learn

\- Joblib



\### Machine Learning



\- Logistic Regression

\- OneHotEncoder

\- StandardScaler

\- Train/Test Split

\- Precision

\- Recall

\- ROC-AUC

\- Calibration Check



\### Frontend



\- HTML

\- CSS

\- JavaScript

\- REST API



\### Deployment



\- Render

\- GitHub



\---



\## Project Structure



```text

recoveriq/

│

├── backend/

│   ├── agent/

│   │   ├── actions.py

│   │   ├── diagnosis.py

│   │   ├── engine.py

│   │   ├── ranker.py

│   │   ├── recovery\_queue.py

│   │   └── safety.py

│   │

│   ├── data/

│   │   ├── payments.csv

│   │   └── recovery\_queue.csv

│   │

│   ├── ml/

│   │   └── train.py

│   │

│   └── api/

│       └── main.py

│

├── frontend/

│   ├── index.html

│   ├── app.js

│   └── style.css

│

└── README.md

