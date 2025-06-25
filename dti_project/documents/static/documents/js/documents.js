document.addEventListener('DOMContentLoaded', function () {
    const coverageChoices = document.querySelectorAll('.coverage-choice');
    const textInputs = document.querySelectorAll('.coverage-text-inputs');

    coverageChoices.forEach(choice => {
        choice.addEventListener('click', function () {
            // Uncheck all and remove 'selected' from all
            coverageChoices.forEach(c => {
                c.classList.remove('selected');
                const rb = c.querySelector('input[type="radio"]');
                if (rb) rb.checked = false;
            });

            // Check this one and add 'selected'
            const radioBtn = choice.querySelector('input[type="radio"]');
            if (radioBtn) {
                radioBtn.checked = true;
                choice.classList.add('selected');
            }

            // Hide all text input groups first
            textInputs.forEach(inputGroup => inputGroup.style.display = 'none');

            // Show the one that matches the selected radio's value (if any)
            const selectedValue = radioBtn ? radioBtn.value : null;
            if (selectedValue) {
                const correspondingInputs = document.getElementById(`id_${selectedValue}`);
                if (correspondingInputs) {
                    correspondingInputs.style.display = 'flex';
                }
            }

        });
    });

    const stepItems = document.querySelectorAll('.form-progress-nav li');

    stepItems.forEach(item => {
        item.addEventListener('click', function () {
            const targetId = this.getAttribute('data-target');
            const targetElement = document.getElementById(targetId);

            if (targetElement) {
                targetElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

});
