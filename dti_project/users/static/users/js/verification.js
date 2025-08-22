document.addEventListener('DOMContentLoaded', function() { 
    const step3 = document.getElementById("step3"); 
    const maskedOutput = document.getElementById("maskedOutput"); 
    const codeInputs = document.querySelectorAll('.code-input');
 
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

    // Auto-navigation logic for code inputs
    codeInputs.forEach((input, index) => {
        input.addEventListener('input', function(e) {
            const value = e.target.value;
            
            // Only allow single digit
            if (value.length > 1) {
                e.target.value = value.slice(0, 1);
            }
            
            // Move to next input if current is filled
            if (e.target.value.length === 1 && index < codeInputs.length - 1) {
                codeInputs[index + 1].focus();
            }
        });

        input.addEventListener('keydown', function(e) {
            // Handle backspace
            if (e.key === 'Backspace') {
                // If current input is empty and not the first input, go to previous
                if (e.target.value === '' && index > 0) {
                    e.preventDefault();
                    codeInputs[index - 1].focus();
                    codeInputs[index - 1].value = '';
                }
                // If current input has value, just clear it (default behavior)
                else if (e.target.value !== '') {
                    e.target.value = '';
                    e.preventDefault();
                }
            }
            
            // Handle arrow keys for navigation
            if (e.key === 'ArrowLeft' && index > 0) {
                e.preventDefault();
                codeInputs[index - 1].focus();
            }
            
            if (e.key === 'ArrowRight' && index < codeInputs.length - 1) {
                e.preventDefault();
                codeInputs[index + 1].focus();
            }
            
            // Only allow numeric input
            if (!/[0-9]/.test(e.key) && 
                !['Backspace', 'Delete', 'Tab', 'ArrowLeft', 'ArrowRight', 'Enter'].includes(e.key)) {
                e.preventDefault();
            }
        });

        // Handle paste events
        input.addEventListener('paste', function(e) {
            e.preventDefault();
            const pasteData = e.clipboardData.getData('text').replace(/\D/g, ''); // Only digits
            
            // Fill inputs starting from current position
            for (let i = 0; i < pasteData.length && (index + i) < codeInputs.length; i++) {
                codeInputs[index + i].value = pasteData[i];
            }
            
            // Focus the next empty input or the last filled one
            const nextEmptyIndex = Math.min(index + pasteData.length, codeInputs.length - 1);
            codeInputs[nextEmptyIndex].focus();
        });
    });
 
    document.getElementById("resendLink").onclick = (e) => { 
        e.preventDefault(); 
        alert("Code resent! (fake demo)"); 
        startCountdown(30);
        
        // Clear all inputs and focus first one
        codeInputs.forEach(input => input.value = '');
        codeInputs[0].focus();
    }; 
 
    // Immediately show step3 on load 
    step3.style.display = "block"; 
    maskedOutput.textContent = "******@example.com"; // or phone placeholder 
    startCountdown(30);
    
    // Focus first input on load
    codeInputs[0].focus();
});