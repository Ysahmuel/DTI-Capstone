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

            // Hide all text input groups and clear their values
            textInputs.forEach(inputGroup => {
                // Clear all inputs inside the inputGroup
                const inputs = inputGroup.querySelectorAll('input, textarea, select');
                inputs.forEach(input => {
                    input.value = '';  // Clear value
                    if (input.type === 'checkbox' || input.type === 'radio') {
                        input.checked = false;  // Uncheck if any
                    }
                });

                inputGroup.style.display = 'none';
            });

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
    const documentsFormDraftBtn = document.querySelector('.form-progress-nav .save-draft-btn')

    if (documentsForm) {
        documentsFormSubmitBtn.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Remove any existing action input
            const existingAction = documentsForm.querySelector('input[name="action"]');
            if (existingAction) {
                existingAction.remove();
            }
            
            // Create and add action input
            const actionInput = document.createElement('input');
            actionInput.type = 'hidden';
            actionInput.name = 'action';
            actionInput.value = 'submitted';
            documentsForm.appendChild(actionInput);
            
            documentsForm.submit();
        });
        
        documentsFormDraftBtn.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Remove any existing action input
            const existingAction = documentsForm.querySelector('input[name="action"]');
            if (existingAction) {
                existingAction.remove();
            }
            
            // Create and add action input
            const actionInput = document.createElement('input');
            actionInput.type = 'hidden';
            actionInput.name = 'action';
            actionInput.value = 'draft';
            documentsForm.appendChild(actionInput);
            
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

    if (uploadFileContainer) {
        const fileInput = uploadFileContainer.querySelector('input[type="file"]');
        
        // Handle click on container or change button
        uploadFileContainer.addEventListener('click', function(e) {
            // Prevent triggering when clicking on the file input itself
            if (e.target !== fileInput) {
                fileInput.click();
            }
        });

        // Handle file selection
        fileInput.addEventListener('change', function() {
            handleFileSelection(this.files[0]);
        });

        // Handle drag and drop
        uploadFileContainer.addEventListener('dragover', function(e) {
            e.preventDefault();
            uploadFileContainer.classList.add('drag-over');
        });

        uploadFileContainer.addEventListener('dragleave', function(e) {
            e.preventDefault();
            uploadFileContainer.classList.remove('drag-over');
        });

        uploadFileContainer.addEventListener('drop', function(e) {
            e.preventDefault();
            uploadFileContainer.classList.remove('drag-over');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                const file = files[0];
                
                // Create a new FileList and assign to input
                const dt = new DataTransfer();
                dt.items.add(file);
                fileInput.files = dt.files;
                
                // Trigger change event
                fileInput.dispatchEvent(new Event('change', { bubbles: true }));
            }
        });

        function handleFileSelection(file) {
            if (!file) {
                resetUploadContainer();
                return;
            }

            // Validate file type
            if (!file.type.startsWith('image/')) {
                alert('Please select an image file.');
                fileInput.value = ''; // Clear the input
                return;
            }

            // Update UI elements
            const dragDropText = uploadFileContainer.querySelector('#drag-drop-text');
            const fileText = uploadFileContainer.querySelector('#file-text');
            const uploadBtn = uploadFileContainer.querySelector('.upload-file-btn');
            const changeBtn = uploadFileContainer.querySelector('.change-image-btn');
            const currentImage = uploadFileContainer.querySelector('#current-image, img');

            // Hide upload button if it exists
            if (uploadBtn) {
                uploadBtn.style.display = 'none';
            }

            // Add filled class
            uploadFileContainer.classList.add('filled');

            // Create and display preview image
            const reader = new FileReader();
            reader.onload = function(e) {
                let img = currentImage;
                
                if (!img) {
                    img = document.createElement('img');
                    img.alt = 'Selected Image';
                    uploadFileContainer.insertBefore(img, dragDropText || fileText);
                }
                
                img.src = e.target.result;
                img.id = 'preview-image';
            };
            reader.readAsDataURL(file);

            // Update text elements
            if (dragDropText) {
                dragDropText.innerHTML = 'Click to <span class="highlighted-span">change image</span>';
            }
            
            if (fileText) {
                fileText.textContent = file.name;
            }

            // Update change button text if it exists
            if (changeBtn) {
                changeBtn.innerHTML = '<i class="fa-solid fa-edit"></i> Change Image';
            }
        }

        function resetUploadContainer() {
            const dragDropText = uploadFileContainer.querySelector('#drag-drop-text');
            const fileText = uploadFileContainer.querySelector('#file-text');
            const uploadBtn = uploadFileContainer.querySelector('.upload-file-btn');
            const previewImg = uploadFileContainer.querySelector('#preview-image');

            uploadFileContainer.classList.remove('filled');
            
            if (uploadBtn) uploadBtn.style.display = 'block';
            if (dragDropText) dragDropText.innerHTML = 'Drag and drop or <span class="highlighted-span">choose file</span> to upload';
            if (fileText) fileText.textContent = 'No file chosen yet.';
            if (previewImg) previewImg.remove();
        }
    }

    const tabItems = document.querySelectorAll('.tab-item');
    const tabContents = document.querySelectorAll('.tab-content');

    tabItems.forEach(tab => {
        tab.addEventListener('click', function() {
            const target = tab.getAttribute('data-tab-target');

            // Remove active class from all tabs and contents
            tabItems.forEach(i => i.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            // Activate clicked tab and corresponding content
            tab.classList.add('active')

            const targetContent = document.querySelector(`.tab-content[data-tab-content="${target}"]`)
            if (targetContent) {
                targetContent.classList.add('active')
            }
        })
    })

});
