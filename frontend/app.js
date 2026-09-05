const API_URL = "https://recoveriq-razorpay-buildathon.onrender.com";


// ===============================
// BASIC HELPERS
// ===============================

function formatMoney(value) {
    const number = Number(value) || 0;

    return "₹" + number.toLocaleString("en-IN", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}


function formatAction(action) {

    const actions = {
        retry_now: "Retry Now",
        retry_scheduled: "Retry Scheduled",
        send_payment_link: "Send Payment Link",
        escalate_to_human: "Escalate"
    };

    return actions[action] || action || "No Action";
}


function createActionBadge(action) {

    let className = "action-badge ";

    if (action === "retry_now") {
        className += "retry-now";
    }
    else if (action === "retry_scheduled") {
        className += "retry-scheduled";
    }
    else if (action === "send_payment_link") {
        className += "send-link";
    }
    else {
        className += "escalate";
    }

    return `
        <span class="${className}">
            ${formatAction(action)}
        </span>
    `;
}


// ===============================
// LOAD RECOVERY QUEUE
// ===============================

async function loadQueue() {

    const tableBody = document.getElementById("queue-body");

    try {

        tableBody.innerHTML = `
            <tr>
                <td colspan="7" class="loading">
                    Loading recovery opportunities...
                </td>
            </tr>
        `;

        console.log("Connecting to:", API_URL);

        const response = await fetch(`${API_URL}/queue`);

        if (!response.ok) {
            throw new Error(
                `Backend returned ${response.status}`
            );
        }

        const data = await response.json();

        console.log("RecoverIQ data received:", data);


        // ===============================
        // UPDATE STATISTICS
        // ===============================

        document.getElementById("total-payments").textContent =
            Number(data.total_payments || 0)
                .toLocaleString("en-IN");


        /*
         * Your backend queue endpoint currently returns
         * the queue itself.
         *
         * Calculate totals from the returned records.
         */

        const payments = data.queue || [];

        let failedAmount = 0;
        let expectedRecovery = 0;

        payments.forEach(payment => {

            failedAmount +=
                Number(payment.amount) || 0;

            expectedRecovery +=
                Number(payment.expected_value) || 0;

        });


        document.getElementById("failed-amount").textContent =
            formatMoney(failedAmount);


        document.getElementById("expected-recovery").textContent =
            formatMoney(expectedRecovery);


        // ===============================
        // DISPLAY TABLE
        // ===============================

        tableBody.innerHTML = "";


        if (payments.length === 0) {

            tableBody.innerHTML = `
                <tr>
                    <td colspan="7" class="loading">
                        No recovery opportunities found.
                    </td>
                </tr>
            `;

            return;
        }


        payments.slice(0, 100).forEach(payment => {

            const row = document.createElement("tr");

            row.style.cursor = "pointer";


            row.innerHTML = `

                <td>
                    ${payment.rank ?? ""}
                </td>

                <td>
                    <strong>
                        ${payment.event_id ?? ""}
                    </strong>
                </td>

                <td>
                    ${formatMoney(payment.amount)}
                </td>

                <td>
                    ${payment.cause ?? ""}
                </td>

                <td>
                    ${
                        (
                            Number(payment.recovery_probability || 0)
                            * 100
                        ).toFixed(1)
                    }%
                </td>

                <td>
                    <strong>
                        ${formatMoney(payment.expected_value)}
                    </strong>
                </td>

                <td>
                    ${createActionBadge(payment.final_action)}
                </td>

            `;


            // Click payment → decision details

            row.addEventListener("click", function () {

                if (payment.event_id) {

                    showDecision(payment.event_id);

                }

            });


            tableBody.appendChild(row);

        });


    }
    catch (error) {

        console.error(
            "RecoverIQ connection error:",
            error
        );


        tableBody.innerHTML = `

            <tr>

                <td colspan="7" class="loading">

                    <strong>
                        Unable to connect to RecoverIQ backend.
                    </strong>

                    <br><br>

                    Backend:
                    ${API_URL}

                    <br><br>

                    Make sure the Render backend is running.

                </td>

            </tr>

        `;

    }

}


// ===============================
// SHOW DECISION
// ===============================

async function showDecision(eventId) {

    console.log(
        "Loading decision:",
        eventId
    );


    try {

        const response =
            await fetch(
                `${API_URL}/decision/${encodeURIComponent(eventId)}`
            );


        if (!response.ok) {

            throw new Error(
                `Decision request failed: ${response.status}`
            );

        }


        const data =
            await response.json();


        console.log(
            "Decision received:",
            data
        );


        // If your HTML has these elements,
        // populate them.

        const modal =
            document.getElementById("decision-modal");


        if (modal) {

            const title =
                document.getElementById("modal-title");

            const details =
                document.getElementById("decision-details");

            const reasoning =
                document.getElementById("reasoning-text");


            if (title) {

                title.textContent =
                    data.event_id;

            }


            if (details) {

                details.innerHTML = `

                    <div class="detail">
                        <span>Amount</span>
                        <strong>
                            ${formatMoney(data.amount)}
                        </strong>
                    </div>

                    <div class="detail">
                        <span>Failure Cause</span>
                        <strong>
                            ${data.cause}
                        </strong>
                    </div>

                    <div class="detail">
                        <span>Recovery Probability</span>
                        <strong>
                            ${(data.recovery_probability * 100).toFixed(1)}%
                        </strong>
                    </div>

                    <div class="detail">
                        <span>Expected Value</span>
                        <strong>
                            ${formatMoney(data.expected_value)}
                        </strong>
                    </div>

                    <div class="detail">
                        <span>Initial Action</span>
                        <strong>
                            ${formatAction(data.initial_action)}
                        </strong>
                    </div>

                    <div class="detail">
                        <span>Final Action</span>
                        <strong>
                            ${formatAction(data.final_action)}
                        </strong>
                    </div>

                    <div class="detail">
                        <span>Safe To Execute</span>
                        <strong>
                            ${data.safe_to_execute ? "YES" : "NO"}
                        </strong>
                    </div>

                    <div class="detail">
                        <span>Intervention Cost</span>
                        <strong>
                            ${formatMoney(data.intervention_cost)}
                        </strong>
                    </div>

                `;

            }


            if (reasoning) {

                reasoning.innerHTML = `

                    <strong>
                        ${
                            data.reasoning?.formula ||
                            "Expected Value = P(recover) × Amount − Intervention Cost"
                        }
                    </strong>

                    <br><br>

                    ${
                        data.reasoning?.calculation ||
                        ""
                    }

                    <br><br>

                    Result:

                    <strong>
                        ${
                            data.reasoning?.result ||
                            formatMoney(data.expected_value)
                        }
                    </strong>

                    <br><br>

                    Safety:

                    ${
                        data.rules_triggered ||
                        "Safety checks passed"
                    }

                `;

            }


            modal.classList.add("show");

        }
        else {

            // Fallback if modal isn't present

            alert(
                `Payment: ${data.event_id}\n\n` +
                `Cause: ${data.cause}\n` +
                `Recovery Probability: ${(data.recovery_probability * 100).toFixed(1)}%\n` +
                `Expected Value: ${formatMoney(data.expected_value)}\n` +
                `Final Action: ${formatAction(data.final_action)}\n` +
                `Safe: ${data.safe_to_execute ? "YES" : "NO"}`
            );

        }

    }
    catch (error) {

        console.error(
            "Decision error:",
            error
        );

        alert(
            "Unable to load decision for " +
            eventId
        );

    }

}


// ===============================
// SIDEBAR NAVIGATION
// ===============================

function setupNavigation() {

    const navItems =
        document.querySelectorAll(".nav-item");


    navItems.forEach(item => {

        item.addEventListener(
            "click",
            function () {

                navItems.forEach(nav => {

                    nav.classList.remove("active");

                });


                this.classList.add("active");


                const page =
                    this.dataset.page;


                document
                    .querySelectorAll(".page")
                    .forEach(section => {

                        section.classList.remove(
                            "active"
                        );

                    });


                const target =
                    document.getElementById(
                        `page-${page}`
                    );


                if (target) {

                    target.classList.add(
                        "active"
                    );

                }

            }
        );

    });

}


// ===============================
// CLOSE MODAL
// ===============================

function setupModal() {

    const modal =
        document.getElementById(
            "decision-modal"
        );


    const closeButton =
        document.getElementById(
            "close-modal"
        );


    if (closeButton) {

        closeButton.addEventListener(
            "click",
            function () {

                modal.classList.remove(
                    "show"
                );

            }
        );

    }


    if (modal) {

        modal.addEventListener(
            "click",
            function (event) {

                if (
                    event.target === modal
                ) {

                    modal.classList.remove(
                        "show"
                    );

                }

            }
        );

    }

}


// ===============================
// REFRESH BUTTON
// ===============================

function setupRefresh() {

    const button =
        document.getElementById(
            "refresh-btn"
        );


    if (!button) return;


    button.addEventListener(
        "click",
        function () {

            loadQueue();

        }
    );

}


// ===============================
// START APPLICATION
// ===============================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        setupNavigation();

        setupModal();

        setupRefresh();

        loadQueue();

    }
);