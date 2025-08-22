document.addEventListener('DOMContentLoaded', function() {
const step1 = document.getElementById("step1");
const step2 = document.getElementById("step2");
const step3 = document.getElementById("step3");
const methodTitle = document.getElementById("methodTitle");
const userInput = document.getElementById("userInput");
const maskedOutput = document.getElementById("maskedOutput");

document.getElementById("chooseEmail").onclick = () => {
  step1.style.display = "none";
  step2.style.display = "block";
  methodTitle.textContent = "Enter your email address";
  userInput.placeholder = "you@example.com";
};

document.getElementById("choosePhone").onclick = () => {
  step1.style.display = "none";
  step2.style.display = "block";
  methodTitle.textContent = "Enter your phone number";
  userInput.placeholder = "+1 234 567 8900";
};

document.getElementById("detailsForm").onsubmit = (e) => {
  e.preventDefault();
  const value = userInput.value.trim();
  if (!value) return;
  step2.style.display = "none";
  step3.style.display = "block";
  maskedOutput.textContent = value;
};

let countdownTimer;

function startCountdown(seconds = 30) {
  const countdownEl = document.getElementById("countdown");
  const resendWrapper = document.getElementById("resendWrapper");
  const resendLink = document.getElementById("resendLink");

  resendWrapper.style.display = "inline";
  resendLink.style.display = "none";
  countdownEl.textContent = seconds;

  clearInterval(countdownTimer);
  countdownTimer = setInterval(() => {
    seconds--;
    countdownEl.textContent = seconds;
    if (seconds <= 0) {
      clearInterval(countdownTimer);
      resendWrapper.style.display = "none";
      resendLink.style.display = "inline";
    }
  }, 1000);
}

document.getElementById("resendLink").onclick = (e) => {
  e.preventDefault();
  alert("Code resent! (fake demo)");
  startCountdown(30);
};

document.getElementById("detailsForm").onsubmit = (e) => {
  e.preventDefault();
  const value = userInput.value.trim();
  if (!value) return;
  step2.style.display = "none";
  step3.style.display = "block";
  maskedOutput.textContent = value;
  startCountdown(30);
};
});