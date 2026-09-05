const API_URL = "http://127.0.0.1:8000";


// Format money in Indian Rupees
function formatMoney(value) {
    const number = Number(value);

    if (!Number.isFinite(number)) {
        return "₹0.00";
    }

    return "₹" + number.toLocaleString("en-IN", {
        maximumFractionDigits: 2
    });
}


// Convert action into readable text
function formatAction(action) {

    const actions = {
        retry_now: "Retry Now",
        retry_scheduled: "Retry Scheduled",
        send_payment_link: "Send Payment Link",
        escalate_to_human: "Escalate"
    };

    return actions[action] || action;
}


// Create action badge
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


// Load recovery queue
async function loadQueue() {

    try {

        const response = await fetch(`${API_URL}/queue`);

        if (!response.ok) {
            throw new Error("Failed to load queue");
        }

        const data = await response.json();

        console.log("Queue received:", data);


        // --------------------------------------------------
        // UPDATE DASHBOARD STATISTICS
        // --------------------------------------------------

        const totalPayments = Number(data.total_payments || 0);

        document.getElementById("total-payments").textContent =
            totalPayments.toLocaleString("en-IN");


        // Get failed amount from API if available.
        // Otherwise calculate it from the queue.
        let totalFailedAmount =
            Number(
                data.total_failed_amount ??
                data.total_failed ??
                data.failed_amount
            );

        if (!Number.isFinite(totalFailedAmount) || totalFailedAmount === 0) {

            totalFailedAmount = data.queue.reduce(
                (sum, payment) => {
                    return sum + Number(payment.amount || 0);
                },
                0
            );
        }


        // Get expected recovery from API if available.
        // Otherwise calculate it from the queue.
        let totalExpectedRecovery =
            Number(
                data.total_expected_recovered_value ??
                data.total_expected_recovery ??
                data.expected_recovery
            );

        if (!Number.isFinite(totalExpectedRecovery) || totalExpectedRecovery === 0) {

            totalExpectedRecovery = data.queue.reduce(
                (sum, payment) => {
                    return sum + Number(payment.expected_value || 0);
                },
                0
            );
        }


        document.getElementById("failed-amount").textContent =
            formatMoney(totalFailedAmount);

        document.getElementById("expected-recovery").textContent =
            formatMoney(totalExpectedRecovery);


        // --------------------------------------------------
        // GET TABLE
        // --------------------------------------------------

        const tableBody = document.getElementById("queue-body");

        tableBody.innerHTML = "";


        // --------------------------------------------------
        // DISPLAY RECOVERY OPPORTUNITIES
        // --------------------------------------------------

        data.queue.forEach(payment => {

            const row = document.createElement("tr");

            row.innerHTML = `
                <td>
                    ${payment.rank}
                </td>

                <td>
                    <strong>
                        ${payment.event_id}
                    </strong>
                </td>

                <td>
                    ${formatMoney(payment.amount)}
                </td>

                <td>
                    ${payment.cause}
                </td>

                <td>
                    ${(Number(payment.recovery_probability || 0) * 100).toFixed(1)}%
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

            tableBody.appendChild(row);
        });


        console.log("Dashboard updated successfully.");

    }
    catch (error) {

        console.error("Error loading queue:", error);

        document.getElementById("queue-body").innerHTML = `
            <tr>
                <td colspan="7" class="loading">
                    Unable to connect to RecoverIQ API.
                    Make sure the backend server is running.
                </td>
            </tr>
        `;
    }
}


// --------------------------------------------------
// REFRESH BUTTON
// --------------------------------------------------

document
    .getElementById("refresh-btn")
    .addEventListener("click", loadQueue);


// --------------------------------------------------
// LOAD DATA WHEN PAGE OPENS
// --------------------------------------------------

loadQueue();