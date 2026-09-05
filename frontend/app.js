const API_URL = "https://recoveriq-razorpay-buildathon.onrender.com";


// ============================================================
// FORMAT MONEY
// ============================================================

function formatMoney(value) {
    const number = Number(value);

    if (isNaN(number)) {
        return "₹0.00";
    }

    return "₹" + number.toLocaleString("en-IN", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}


// ============================================================
// FORMAT ACTION
// ============================================================

function formatAction(action) {

    const actions = {
        retry_now: "Retry Now",
        retry_scheduled: "Retry Scheduled",
        send_payment_link: "Send Payment Link",
        escalate_to_human: "Escalate"
    };

    return actions[action] || action;
}


// ============================================================
// ACTION BADGE
// ============================================================

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


// ============================================================
// LOAD RECOVERY QUEUE
// ============================================================

async function loadQueue() {

    const refreshButton = document.getElementById("refresh-btn");
    const queueBody = document.getElementById("queue-body");

    try {

        // Loading state
        if (refreshButton) {
            refreshButton.disabled = true;
            refreshButton.innerHTML = "↻ &nbsp; Loading...";
        }

        queueBody.innerHTML = `
            <tr>
                <td colspan="7" class="loading">
                    Loading recovery opportunities...
                </td>
            </tr>
        `;


        // Call backend
        const response = await fetch(`${API_URL}/queue`);


        if (!response.ok) {
            throw new Error(
                `API returned status ${response.status}`
            );
        }


        const data = await response.json();

        console.log("RecoverIQ Queue:", data);


        // ====================================================
        // UPDATE STATISTICS
        // ====================================================

        document.getElementById("total-payments").textContent =
            Number(data.total_payments || 0).toLocaleString("en-IN");


        document.getElementById("failed-amount").textContent =
            formatMoney(data.total_failed_amount);


        document.getElementById("expected-recovery").textContent =
            formatMoney(data.total_expected_recovered_value);


        // ====================================================
        // UPDATE TABLE
        // ====================================================

        queueBody.innerHTML = "";


        if (!data.queue || data.queue.length === 0) {

            queueBody.innerHTML = `
                <tr>
                    <td colspan="7" class="loading">
                        No recovery opportunities found.
                    </td>
                </tr>
            `;

            return;
        }


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
                    ${(Number(payment.recovery_probability) * 100).toFixed(1)}%
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


            queueBody.appendChild(row);

        });


        // Update live status
        updateSystemStatus(true);

    }

    catch (error) {

        console.error("RecoverIQ API Error:", error);


        queueBody.innerHTML = `
            <tr>
                <td colspan="7" class="loading">

                    Unable to connect to RecoverIQ API.

                    <br>

                    <small>
                        Make sure the FastAPI backend is running on
                        http://127.0.0.1:8000
                    </small>

                </td>
            </tr>
        `;


        updateSystemStatus(false);

    }

    finally {

        if (refreshButton) {

            refreshButton.disabled = false;

            refreshButton.innerHTML =
                "↻ &nbsp; Refresh";

        }

    }
}


// ============================================================
// SYSTEM STATUS
// ============================================================

function updateSystemStatus(online) {

    const liveIndicator =
        document.querySelector(".live-indicator");

    if (!liveIndicator) {
        return;
    }


    if (online) {

        liveIndicator.innerHTML = `
            <span></span>
            LIVE
        `;

        liveIndicator.classList.remove("offline");

    }
    else {

        liveIndicator.innerHTML = `
            <span></span>
            OFFLINE
        `;

        liveIndicator.classList.add("offline");

    }
}


// ============================================================
// REFRESH BUTTON
// ============================================================

const refreshButton =
    document.getElementById("refresh-btn");


if (refreshButton) {

    refreshButton.addEventListener(
        "click",
        function () {

            console.log("Refreshing RecoverIQ queue...");

            loadQueue();

        }
    );

}


// ============================================================
// SIDEBAR NAVIGATION
// ============================================================

const navigationItems =
    document.querySelectorAll(".nav-item");


navigationItems.forEach(item => {

    item.addEventListener("click", function () {

        // Remove active state
        navigationItems.forEach(nav => {
            nav.classList.remove("active");
        });


        // Add active state
        this.classList.add("active");


        const section =
            this.dataset.section;


        console.log(
            "RecoverIQ navigation:",
            section
        );


        // ====================================================
        // NAVIGATION BEHAVIOR
        // ====================================================

        if (section === "queue") {

            window.scrollTo({
                top: 0,
                behavior: "smooth"
            });

        }


        else if (section === "decision") {

            const insight =
                document.querySelector(".insight-card");

            if (insight) {

                insight.scrollIntoView({
                    behavior: "smooth",
                    block: "center"
                });

            }

            showNotification(
                "Decision Engine",
                "RecoverIQ is using AI-based recovery decisions."
            );

        }


        else if (section === "analytics") {

            const stats =
                document.querySelector(".stats-grid");

            if (stats) {

                stats.scrollIntoView({
                    behavior: "smooth",
                    block: "center"
                });

            }

            showNotification(
                "Recovery Analytics",
                "Analytics are calculated from the recovery queue."
            );

        }


        else if (section === "failure") {

            const queue =
                document.querySelector(".queue-section");

            if (queue) {

                queue.scrollIntoView({
                    behavior: "smooth",
                    block: "center"
                });

            }

            showNotification(
                "Failure Log",
                "Payment failures are classified by the diagnosis engine."
            );

        }

    });

});


// ============================================================
// NOTIFICATION
// ============================================================

function showNotification(title, message) {

    // Remove existing notification
    const old =
        document.querySelector(".recoveriq-notification");

    if (old) {
        old.remove();
    }


    const notification =
        document.createElement("div");


    notification.className =
        "recoveriq-notification";


    notification.innerHTML = `
        <strong>${title}</strong>
        <span>${message}</span>
    `;


    document.body.appendChild(notification);


    // Animate in
    setTimeout(() => {

        notification.classList.add("show");

    }, 10);


    // Remove after 3 seconds
    setTimeout(() => {

        notification.classList.remove("show");

        setTimeout(() => {

            notification.remove();

        }, 300);

    }, 3000);

}


// ============================================================
// INITIAL LOAD
// ============================================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        console.log(
            "RecoverIQ frontend initialized."
        );

        loadQueue();

    }
);