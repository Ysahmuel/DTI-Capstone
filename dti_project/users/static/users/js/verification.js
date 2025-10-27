document.addEventListener('DOMContentLoaded', function () {
    // Select forgot-password form first
    const form = document.querySelector('#forgot-password-form') || document.querySelector('#register-form');
    const maskedOutput = document.getElementById("maskedOutput");
    const codeInputs = document.querySelectorAll('.code-input');
    const resendBtn = document.getElementById("resend-btn");
    let countdownTimer;

    // ----------------------
    // Submit handler
    // ----------------------
    if (form) {
        form.addEventListener('submit', async function (e) {
            e.preventDefault();
            const formData = new FormData(form);

            console.log("=== FORM DATA ===");
            for (let [key, value] of formData.entries()) {
                console.log(`${key}: ${value}`);
            }

            try {
                const response = await fetch(form.action, {
                    method: "POST",
                    body: formData,
                    headers: {
                        "X-Requested-With": "XMLHttpRequest",
                        "X-CSRFToken": getCSRFToken(),
                    }
                });

                console.log("Response status:", response.status);
                const data = await response.json();
                console.log("Response data:", data);

                if (data.success) {
                    // Show verification modal
                    const verificationContainer = document.querySelector('.verification-container');
                    if (verificationContainer) {
                        verificationContainer.style.display = "flex";
                    }

                    // Show masked email in modal
                    if (maskedOutput && data.masked_email) {
                        maskedOutput.textContent = data.masked_email;
                    }

                    startCountdown(30);

                    // Clear and focus code inputs
                    const modalCodeInputs = document.querySelectorAll('.code-input');
                    modalCodeInputs.forEach(input => input.value = '');
                    if (modalCodeInputs.length > 0) {
                        modalCodeInputs[0].focus();
                    }

                } else {
                    // Show error messages from backend if any
                    if (data.messages_html) {
                        const alertsContainer = document.querySelector('.alerts-container');
                        if (alertsContainer) {
                            alertsContainer.outerHTML = data.messages_html;
                        } else {
                            document.querySelector('.backdrop-layer')
                                .insertAdjacentHTML('afterbegin', data.messages_html);
                        }
                    } else {
                        alert("Something went wrong. Please try again.");
                    }
                }
            } catch (error) {
                console.error("Error submitting form:", error);
                alert("Something went wrong. Please try again.");
            }
        });
    }

    // ----------------------
    // Countdown timer
    // ----------------------
    function startCountdown(seconds = 30) {
        const countdownEl = document.getElementById("countdown");
        const resendWrapper = document.getElementById("resendWrapper");
        if (resendWrapper && resendBtn && countdownEl) {
            resendWrapper.style.display = "inline";
            resendBtn.style.display = "none";
            countdownEl.textContent = seconds;

            clearInterval(countdownTimer);
            countdownTimer = setInterval(() => {
                seconds--;
                countdownEl.textContent = seconds;
                if (seconds <= 0) {
                    clearInterval(countdownTimer);
                    resendWrapper.style.display = "none";
                    resendBtn.style.display = "inline";
                }
            }, 1000);
        }
    }

    // ----------------------
    // Resend code button
    // ----------------------
    if (resendBtn) {
        resendBtn.addEventListener('click', async function () {
            try {
                const response = await fetch(`/users/resend-code/`, {
                    method: "POST",
                    headers: {
                        'X-CSRFToken': getCSRFToken(),
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });

                const data = await response.json();
                if (data.success) {
                    console.log('Code resent successfully');
                    startCountdown(30);
                }
            } catch (error) {
                console.error('Error: failed to resend code', error);
            }
        });
    }

    // ----------------------
    // Code input auto-navigation
    // ----------------------
    codeInputs.forEach((input, index) => {
        input.addEventListener('input', function (e) {
            e.target.value = e.target.value.replace(/\D/g, '');
            if (e.target.value.length === 1 && index < codeInputs.length - 1) {
                codeInputs[index + 1].focus();
            }
        });

        input.addEventListener('keydown', function (e) {
            if (e.key === 'Backspace' && e.target.value === '' && index > 0) {
                codeInputs[index - 1].focus();
            }
        });
    });

    // ----------------------
    // Verify code
    // ----------------------
    document.addEventListener('click', async function (e) {
        if (e.target.matches('.btn-verify')) {
            e.preventDefault();
            const modalCodeInputs = document.querySelectorAll('.code-input');
            const code = Array.from(modalCodeInputs).map(i => i.value).join('');

            if (code.length !== 6) {
                alert("Please enter the full 6-digit code.");
                return;
            }

            // determine verification type
            const verification_type = (form && form.id === "forgot-password-form")
                ? "reset_password"
                : "registration";

            try {
                const response = await fetch('/users/verify-user/', {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/x-www-form-urlencoded",
                        "X-CSRFToken": getCSRFToken(),
                        "X-Requested-With": "XMLHttpRequest",
                    },
                    body: new URLSearchParams({
                        code: code,
                        verification_type: verification_type
                    })
                });

                const data = await response.json();
                if (data.success) {
                    alert("✅ Verification successful!");
                    window.location.href = data.redirect || (
                        verification_type === "reset_password"
                            ? "/users/reset-password/"
                            : "/dashboard/"
                    );
                } else {
                    alert("❌ " + (data.error || data.message || "Verification failed"));
                }

            } catch (error) {
                console.error("Error verifying code:", error);
                alert("Something went wrong. Please try again.");
            }
        }
    });

    // ----------------------
    // CSRF helper
    // ----------------------
    function getCSRFToken() {
        const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]");
        return csrfToken ? csrfToken.value : '';
    }
});
