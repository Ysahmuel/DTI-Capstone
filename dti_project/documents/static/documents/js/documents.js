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

    function checkStepCompletion() {
        const stepItems = document.querySelectorAll('[data-target]');
        let totalRequiredFields = 0;
        let completedFields = 0;

        stepItems.forEach(item => {
            const stepId = item.getAttribute('data-target');
            const stepFieldset = document.getElementById(stepId);
            if (!stepFieldset) return;

            let allFilled = true;

            if (stepId === 'coverage-fieldset') {
            // Special rule for Coverage fieldset
            const selectedCoverage = stepFieldset.querySelector('input[name="coverage"]:checked');

            if (!selectedCoverage) {
                allFilled = false;
            } else {
                const selectedValue = selectedCoverage.value;
                const correspondingInputs = stepFieldset.querySelectorAll(`#id_${selectedValue} input, #id_${selectedValue} textarea, #id_${selectedValue} select`);

                correspondingInputs.forEach(input => {
                if (!input.value.trim()) {
                    allFilled = false;
                }

                // Attach listeners
                input.removeEventListener('input', checkStepCompletion);
                input.removeEventListener('change', checkStepCompletion);
                input.addEventListener('input', checkStepCompletion);
                input.addEventListener('change', checkStepCompletion);
                });
            }

            // Add listener to coverage radios
            const radios = stepFieldset.querySelectorAll('input[name="coverage"]');
            radios.forEach(radio => {
                radio.removeEventListener('change', checkStepCompletion);
                radio.addEventListener('change', checkStepCompletion);
            });

            } else {
            // Normal logic
            const requiredFields = stepFieldset.querySelectorAll('.documents-form [required]');
            const allInputs = stepFieldset.querySelectorAll('.documents-form input, .documents-form textarea, .documents-form select');

            if (requiredFields.length > 0) {
                requiredFields.forEach(field => {
                totalRequiredFields++;

                let isFieldFilled = false;

                if (field.type === 'radio' || field.type === 'checkbox') {
                    const group = stepFieldset.querySelectorAll(`[name="${field.name}"]`);
                    const isChecked = Array.from(group).some(input => input.checked);
                    if (isChecked) isFieldFilled = true;
                    else allFilled = false;
                } else {
                    if (field.value.trim()) isFieldFilled = true;
                    else allFilled = false;
                }

                if (isFieldFilled) completedFields++;

                field.removeEventListener('input', checkStepCompletion);
                field.removeEventListener('change', checkStepCompletion);
                field.addEventListener('input', checkStepCompletion);
                field.addEventListener('change', checkStepCompletion);
                });
            } else {
                allInputs.forEach(input => {
                if (input.type === 'radio' || input.type === 'checkbox') {
                    const group = stepFieldset.querySelectorAll(`[name="${input.name}"]`);
                    const isChecked = Array.from(group).some(i => i.checked);
                    if (!isChecked) allFilled = false;
                } else {
                    if (!input.value.trim()) allFilled = false;
                }

                input.removeEventListener('input', checkStepCompletion);
                input.removeEventListener('change', checkStepCompletion);
                input.addEventListener('input', checkStepCompletion);
                input.addEventListener('change', checkStepCompletion);
                });
            }
            }

            // Visuals: check / circle swap
            const stepCircle = item.querySelector('.step-circle');
            const existingCheckIcon = item.querySelector('.fa-check');

            if (allFilled) {
            item.classList.add('complete');

            if (!existingCheckIcon) {
                if (stepCircle) stepCircle.remove();
                const checkIcon = document.createElement('i');
                checkIcon.classList.add('fa-solid', 'fa-check', 'step-check-icon');
                item.insertBefore(checkIcon, item.firstChild);
            }
            } else {
            item.classList.remove('complete');
            if (existingCheckIcon) existingCheckIcon.remove();
            if (!item.querySelector('.step-circle')) {
                const newCircle = document.createElement('span');
                newCircle.classList.add('step-circle');
                item.insertBefore(newCircle, item.firstChild);
            }
            }

        });

        const progressPercentage = totalRequiredFields > 0 ? Math.round((completedFields / totalRequiredFields) * 100) : 0;
        updateProgress(progressPercentage);
    }

    function updateProgress(percentage) {
        const completionPercentage = document.querySelector('.completion-percentage');

        const valueElement = completionPercentage.querySelector('.value');
        const fillElement = completionPercentage.querySelector('.fill');
        const statusElement = completionPercentage.querySelector('.status');
        const valueSpan = completionPercentage.querySelector('.value span');

        // Calculate angle for circular progress (360 degrees = 100%)
        const angle = (percentage / 100) * 360;

        // Update CSS custom properties
        valueElement.style.setProperty('--progress-angle', `${angle}deg`);
        fillElement.style.setProperty('--progress-width', `${percentage}%`);

        // Update text content
        valueSpan.textContent = `${percentage}%`;
        valueElement.setAttribute('data-percentage', percentage);

        // Update status text
        if (percentage === 100) {
            statusElement.textContent = 'Complete';
        } else if (percentage >= 75) {
            statusElement.textContent = 'Nearly Complete';
        } else if (percentage >= 50) {
            statusElement.textContent = 'In Progress';
        } else {
            statusElement.textContent = 'Incomplete';
        }
    }

    checkStepCompletion();

    const documentsForm = document.querySelector('.documents-form');
    const documentsFormSubmitBtn = document.querySelector('.form-progress-nav .submit-btn');

    documentsFormSubmitBtn.addEventListener('click', (e) => {
        e.preventDefault();

        if (documentsForm) {
            documentsForm.submit()
        }
    })

});
