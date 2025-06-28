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

            const requiredFields = stepFieldset.querySelectorAll('.documents-form [required]');
            let allFilled = true; // Start with true, set to false if any field is empty

            requiredFields.forEach(field => {
                totalRequiredFields++; // Count total required fields
                
                let isFieldFilled = false;
                
                if (field.type === 'radio' || field.type === 'checkbox') {
                    const group = stepFieldset.querySelectorAll(`[name="${field.name}"]`);
                    const isChecked = Array.from(group).some(input => input.checked);
                    if (!isChecked) {
                        allFilled = false;
                    } else {
                        isFieldFilled = true;
                    }
                } else {
                    if (!field.value.trim()) {
                        allFilled = false;
                    } else {
                        isFieldFilled = true;
                    }
                }
                
                // Count completed fields
                if (isFieldFilled) {
                    completedFields++;
                }
                
                // Remove duplicate event listeners by checking if already added
                field.removeEventListener('input', checkStepCompletion);
                field.removeEventListener('change', checkStepCompletion);
                field.addEventListener('input', checkStepCompletion);
                field.addEventListener('change', checkStepCompletion);
            });

            // If no required fields exist, don't mark as complete
            if (requiredFields.length === 0) {
                allFilled = false;
            }
            
            if (allFilled) {
                item.classList.add('complete');
            } else {
                item.classList.remove('complete');
            }
        });

        // Calculate and update progress percentage
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
