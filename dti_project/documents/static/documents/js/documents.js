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
                totalRequiredFields++;

                const selectedCoverage = stepFieldset.querySelector('input[name="coverage"]:checked');
                if (selectedCoverage) {
                    completedFields++;

                    const selectedValue = selectedCoverage.value;
                    const dependentInputs = stepFieldset.querySelectorAll(`#id_${selectedValue} input, #id_${selectedValue} textarea, #id_${selectedValue} select`);
                    dependentInputs.forEach(input => {
                        if (input.disabled || input.offsetParent === null) return;

                        totalRequiredFields++;
                        if (input.value.trim()) completedFields++;
                        else allFilled = false;

                        input.removeEventListener('input', checkStepCompletion);
                        input.removeEventListener('change', checkStepCompletion);
                        input.addEventListener('input', checkStepCompletion);
                        input.addEventListener('change', checkStepCompletion);
                    });

                } else {
                    allFilled = false;
                }

                const radios = stepFieldset.querySelectorAll('input[name="coverage"]');
                radios.forEach(radio => {
                    radio.removeEventListener('change', checkStepCompletion);
                    radio.addEventListener('change', checkStepCompletion);
                });

            } else {
                const allFields = stepFieldset.querySelectorAll('input, textarea, select');
                const requiredFields = stepFieldset.querySelectorAll('[required]');

                // Mark fieldset as optional if no required fields
                if (requiredFields.length === 0) {
                    item.classList.add('optional');
                } else {
                    item.classList.remove('optional');
                }

                allFields.forEach(field => {
                    if (field.disabled || field.offsetParent === null) return;

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
            }

            // Visual indicator logic
            const stepCircle = item.querySelector('.step-circle');
            const existingCheckIcon = item.querySelector('.fa-check');

            if (allFilled && totalRequiredFields > 0) {
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

        const progressPercentage = totalRequiredFields > 0
            ? Math.round((completedFields / totalRequiredFields) * 100)
            : 0;

        updateProgress(progressPercentage);
    }

    function updateProgress(percentage) {
        const completionPercentage = document.querySelector('.completion-percentage');
        const valueElement = completionPercentage.querySelector('.value');
        const fillElement = completionPercentage.querySelector('.fill');
        const statusElement = completionPercentage.querySelector('.status');
        const valueSpan = completionPercentage.querySelector('.value span');

        const angle = (percentage / 100) * 360;

        valueElement.style.setProperty('--progress-angle', `${angle}deg`);
        fillElement.style.setProperty('--progress-width', `${percentage}%`);

        valueSpan.textContent = `${percentage}%`;
        valueElement.setAttribute('data-percentage', percentage);

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

    // Initial run
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
