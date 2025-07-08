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
            let stepRequiredFields = 0;
            let stepCompletedFields = 0;

            if (stepId === 'coverage-fieldset') {
                stepRequiredFields++;

                const selectedCoverage = stepFieldset.querySelector('input[name="coverage"]:checked');
                if (selectedCoverage) {
                    stepCompletedFields++;

                    const selectedValue = selectedCoverage.value;
                    const dependentInputs = stepFieldset.querySelectorAll(`#id_${selectedValue} input, #id_${selectedValue} textarea, #id_${selectedValue} select`);
                    dependentInputs.forEach(input => {
                        if (input.disabled || input.offsetParent === null) return;

                        stepRequiredFields++;
                        if (input.value.trim()) stepCompletedFields++;
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
                const requiredFields = stepFieldset.querySelectorAll('[required]');

                if (requiredFields.length === 0) {
                    item.classList.add('optional');
                } else {
                    item.classList.remove('optional');
                }

                const allFields = stepFieldset.querySelectorAll('input, textarea, select');

                allFields.forEach(field => {
                    if (field.disabled || field.offsetParent === null) return;

                    const isRequired = field.hasAttribute('required');

                    // Only add required fields to progress totals
                    if (isRequired) {
                        stepRequiredFields++;

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

                        if (isFieldFilled) stepCompletedFields++;
                    } else {
                        // For optional steps, check if every visible+enabled field is filled to consider step "complete"
                        if (item.classList.contains('optional')) {
                            if (field.value.trim()) {
                                // do nothing
                            } else {
                                allFilled = false;
                            }
                        }
                    }

                    field.removeEventListener('input', checkStepCompletion);
                    field.removeEventListener('change', checkStepCompletion);
                    field.addEventListener('input', checkStepCompletion);
                    field.addEventListener('change', checkStepCompletion);
                });
            }

            totalRequiredFields += stepRequiredFields;
            completedFields += stepCompletedFields;

            // Visual indicator logic
            const stepCircle = item.querySelector('.step-circle');
            const existingCheckIcon = item.querySelector('.fa-check');

            if (allFilled && (stepRequiredFields === 0 || stepCompletedFields === stepRequiredFields)) {
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
        if (!completionPercentage) return;  // Exit if not on this page

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
    if (typeof checkStepCompletion === "function") {
        checkStepCompletion();
    }

    const documentsForm = document.querySelector('.documents-form');
    const documentsFormSubmitBtn = document.querySelector('.form-progress-nav .submit-btn');

    if (documentsForm && documentsFormSubmitBtn) {
        documentsFormSubmitBtn.addEventListener('click', (e) => {
            e.preventDefault();
            documentsForm.submit();
        });
    }

    // Fill empty details in document detail pages
    const documentsDetailsList = document.querySelector('.details-list');
    if (documentsDetailsList) {
        const emptyValues = Array.from(documentsDetailsList.querySelectorAll('.label-value-row p'))
            .filter(p => !p.textContent.trim());

        emptyValues.forEach(value => {
            value.textContent = '-';
        });
    }

    const uploadFileContainer = document.querySelector('.upload-image-container');
    
    uploadFileContainer.addEventListener('click', function() {
        const input = uploadFileContainer.querySelector('input[type="file"]');
        const dragDropChooseText = uploadFileContainer.querySelector('#drag-drop-text');
        const fileText = uploadFileContainer.querySelector('#file-text');
        const uploadBtn = uploadFileContainer.querySelector('.upload-file-btn')

        input.click()

        input.addEventListener('change', function () {
            if (input.files.length > 0) {
                const file = input.files[0];
                uploadBtn.style.display = 'none';

                uploadFileContainer.classList.add('filled');

                // Check if it's an image
                if (file.type.startsWith('image/')) {
                    const reader = new FileReader();
                    reader.onload = function (e) {
                        const img = document.createElement('img');
                        img.src = e.target.result;
                        img.alt = 'Selected Image';

                        // Remove previous image if re-selecting
                        const oldImg = uploadFileContainer.querySelector('img');
                        if (oldImg) {
                            oldImg.remove();
                        }

                        // Insert image above file name text
                        uploadFileContainer.insertBefore(img, dragDropChooseText);
                    };
                    reader.readAsDataURL(file);

                    dragDropChooseText.innerHTML = 'Click to <span class="highlighted-span">change image</span>';
                    fileText.textContent = file.name;
                }
            } else {
                uploadFileContainer.classList.remove('filled');
                dragDropChooseText.innerHTML = '<h3>Drag and drop or <span class="highlighted-span">choose file</span> to upload</h3>'
                fileText.textContent = 'No file chosen yet';
            }
        });

    })

});
