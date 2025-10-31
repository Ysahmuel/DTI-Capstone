document.addEventListener('DOMContentLoaded', function () {
    // Debug: Check what data-label values are being generated
    console.log('Available formsets:', document.querySelectorAll("fieldset[data-label]"));
    document.querySelectorAll("fieldset[data-label]").forEach(fieldset => {
        console.log('Fieldset data-label:', fieldset.dataset.label);

        // Check if management form exists
        const managementForm = fieldset.querySelector("input[name$='-TOTAL_FORMS']");
        console.log('Management form found:', managementForm);
        if (managementForm) {
            console.log('Management form name:', managementForm.name);
        }
    });

    document.querySelectorAll("fieldset[data-label]").forEach(fieldset => {
        const addButton = fieldset.querySelector(".add-btn");
        const formGrid = fieldset.querySelector(".step-grid");
        const previewList = document.querySelector(`#${fieldset.dataset.label}-preview-list`);
        const managementForm = fieldset.querySelector("input[name$='-TOTAL_FORMS']");
        const formsetPrefix = fieldset.dataset.label.replace('-', '_');

        let formCount = parseInt(managementForm.value) || 0;

        // -------------------------------
        // DATE RANGE VALIDATION
        // -------------------------------
        function validateDateRange() {
            const startDateInput = formGrid.querySelector("input[name*='start_date'], input[name*='date_from']");
            const endDateInput = formGrid.querySelector("input[name*='end_date'], input[name*='date_to']");

            if (startDateInput && endDateInput && startDateInput.value && endDateInput.value) {
                const startDate = new Date(startDateInput.value);
                const endDate = new Date(endDateInput.value);

                if (endDate < startDate) {
                    let errorDiv = endDateInput.parentElement.querySelector('.date-error');
                    if (!errorDiv) {
                        errorDiv = document.createElement('div');
                        errorDiv.className = 'date-error';
                        errorDiv.style.color = 'red';
                        errorDiv.style.fontSize = '0.875rem';
                        errorDiv.style.marginTop = '0.25rem';
                        endDateInput.parentElement.appendChild(errorDiv);
                    }
                    errorDiv.textContent = 'End date cannot be earlier than start date';
                    return false;
                } else {
                    const errorDiv = endDateInput.parentElement.querySelector('.date-error');
                    if (errorDiv) errorDiv.remove();
                }
            }
            return true;
        }

        // -------------------------------
        // STRICTER DATE BEHAVIOR
        // -------------------------------
        function applyStricterDateRules() {
            const startDateInput = formGrid.querySelector("input[name*='start_date'], input[name*='date_from']");
            const endDateInput = formGrid.querySelector("input[name*='end_date'], input[name*='date_to']");

            if (!startDateInput || !endDateInput) return;

            const endDateLabel = endDateInput.closest(".form-group, .form-field, div")?.querySelector("label");

            const originalEndLabel = endDateLabel ? endDateLabel.textContent : "";

            // When start date is empty
            if (!startDateInput.value) {
                endDateInput.disabled = true;
                endDateInput.value = "";
                endDateInput.removeAttribute("min");

                if (endDateLabel) {
                    endDateLabel.textContent = `${originalEndLabel} (fill in start date first)`;
                }
            }

            // When start date changes
            startDateInput.addEventListener("change", function () {
                if (startDateInput.value) {
                    // Enable end date
                    endDateInput.disabled = false;
                    endDateInput.min = startDateInput.value;

                    // Restore original label
                    if (endDateLabel) {
                        endDateLabel.textContent = originalEndLabel;
                    }

                    // Auto-correct invalid end dates
                    if (endDateInput.value && endDateInput.value < startDateInput.value) {
                        endDateInput.value = "";
                    }

                } else {
                    // Disable end date again
                    endDateInput.disabled = true;
                    endDateInput.value = "";
                    endDateInput.removeAttribute("min");

                    // Add warning text
                    if (endDateLabel) {
                        endDateLabel.textContent = `${originalEndLabel} (fill in start date first)`;
                    }
                }

                validateRequiredFields();
            });

            endDateInput.addEventListener("change", function () {
                if (endDateInput.value && endDateInput.value < startDateInput.value) {
                    endDateInput.value = "";
                }
                validateRequiredFields();
            });
        }


        // Apply stricter date behavior
        applyStricterDateRules();

        // -------------------------------
        // REQUIRED FIELD VALIDATION
        // -------------------------------
        function validateRequiredFields() {
            const requiredInputs = formGrid.querySelectorAll("input[required], select[required], textarea[required]");

            if (requiredInputs.length === 0) {
                const dateRangeValid = validateDateRange();
                addButton.disabled = !dateRangeValid;
                addButton.style.opacity = dateRangeValid ? "1" : "0.5";
                addButton.style.cursor = dateRangeValid ? "pointer" : "not-allowed";
                return;
            }

            let allFilled = true;

            requiredInputs.forEach(input => {
                const value = input.value.trim();
                if (!value) allFilled = false;
            });

            const dateRangeValid = validateDateRange();

            if (allFilled && dateRangeValid) {
                addButton.disabled = false;
                addButton.style.opacity = "1";
                addButton.style.cursor = "pointer";
            } else {
                addButton.disabled = true;
                addButton.style.opacity = "0.5";
                addButton.style.cursor = "not-allowed";
            }
        }

        validateRequiredFields();

        // -------------------------------
        // INPUT EVENT LISTENERS
        // -------------------------------
        const allInputs = formGrid.querySelectorAll("input, select, textarea");
        allInputs.forEach(input => {
            input.addEventListener("input", validateRequiredFields);
            input.addEventListener("change", validateRequiredFields);
            input.addEventListener("blur", validateRequiredFields);

            // Numeric restrictions for specific fields
            if (
                input.name.includes('contact_number') ||
                input.name.includes('mobile_number') ||
                input.name.includes('telephone') ||
                input.name.includes('zip_code') ||
                input.name.includes('fax_number')
            ) {
                input.addEventListener("keypress", function (e) {
                    if (e.key && !/^\d$/.test(e.key)) e.preventDefault();
                });

                input.addEventListener("paste", function (e) {
                    e.preventDefault();
                    const pasted = (e.clipboardData || window.clipboardData).getData('text');
                    const clean = pasted.replace(/\D/g, '');
                    const start = this.selectionStart;
                    const end = this.selectionEnd;
                    const current = this.value;
                    this.value = current.substring(0, start) + clean + current.substring(end);
                    this.selectionStart = this.selectionEnd = start + clean.length;
                    validateRequiredFields();
                });

                input.addEventListener("input", function () {
                    const cursorPos = this.selectionStart;
                    const before = this.value.length;
                    this.value = this.value.replace(/\D/g, '');
                    const after = this.value.length;
                    const diff = before - after;
                    this.selectionStart = this.selectionEnd = Math.max(0, cursorPos - diff);
                });
            }

            if (input.type === 'date') {
                input.addEventListener("change", function () {
                    validateDateRange();
                    validateRequiredFields();
                });
            }
        });

        // -------------------------------
        // FORMSET HIDDEN INPUTS
        // -------------------------------
        function updateTotalForms() {
            managementForm.value = formCount;
        }

        function extractFieldName(templateName) {
            return templateName.replace('template_', '');
        }

        function createHiddenFormset(formData, index) {
            const hiddenContainer = document.createElement("div");
            hiddenContainer.classList.add("hidden-formset");
            hiddenContainer.style.display = "none";

            const templateInputs = formGrid.querySelectorAll("input, select, textarea");

            templateInputs.forEach(input => {
                const fieldName = extractFieldName(input.name);
                const hiddenInput = document.createElement("input");
                hiddenInput.type = "hidden";
                hiddenInput.name = `${formsetPrefix}-${index}-${fieldName}`;
                hiddenInput.value = formData[input.name] || '';
                hiddenContainer.appendChild(hiddenInput);
            });

            const idInput = document.createElement("input");
            idInput.type = "hidden";
            idInput.name = `${formsetPrefix}-${index}-id`;
            idInput.value = "";
            hiddenContainer.appendChild(idInput);

            const deleteInput = document.createElement("input");
            deleteInput.type = "hidden";
            deleteInput.name = `${formsetPrefix}-${index}-DELETE`;
            deleteInput.value = "";
            hiddenContainer.appendChild(deleteInput);

            return hiddenContainer;
        }

        // -------------------------------
        // PREVIEW ITEM ADD
        // -------------------------------
        function addToPreview() {
            const formData = {};
            const inputs = formGrid.querySelectorAll("input, select, textarea");

            let hasValue = false;
            inputs.forEach(input => {
                if (input.value.trim()) hasValue = true;
                formData[input.name] = input.value.trim();
            });

            if (!hasValue) {
                alert("Please fill in at least one field before adding.");
                return;
            }

            if (!validateDateRange()) {
                alert("Please correct the date range. End date cannot be earlier than start date.");
                return;
            }

            const previewItem = document.createElement("li");
            previewItem.classList.add("preview-item");
            previewItem.dataset.formIndex = formCount;

            const values = Object.values(formData).filter(val => val.trim());
            const titleText = values.length >= 2 ? `${values[1]} - ${values[0]}` : values[0] || 'New Item';

            const title = document.createElement("strong");
            title.textContent = titleText;
            previewItem.appendChild(title);

            if (values.length >= 3) {
                const startDate = values[2];
                const endDate = values[3] || "Present";
                const period = document.createElement("p");
                period.classList.add("period");
                period.textContent = `(${startDate} - ${endDate})`;
                previewItem.appendChild(period);
            }

            previewItem.appendChild(createHiddenFormset(formData, formCount));

            const removeBtn = document.createElement("button");
            removeBtn.type = "button";
            removeBtn.classList.add("remove-btn");
            const icon = document.createElement("div");
            icon.className = "fa-solid fa-xmark";
            removeBtn.appendChild(icon);

            removeBtn.addEventListener("click", function () {
                previewItem.remove();
                updateFormIndices();
                // Notify progress bar of formset change
                document.dispatchEvent(new CustomEvent('formsetItemChanged'));
            });

            previewItem.appendChild(removeBtn);

            previewList.appendChild(previewItem);

            inputs.forEach(input => {
                input.value = "";
                const errorDiv = input.parentElement.querySelector('.date-error');
                if (errorDiv) errorDiv.remove();
            });

            formCount++;
            updateTotalForms();
            validateRequiredFields();
            
            // Notify progress bar of formset change
            document.dispatchEvent(new CustomEvent('formsetItemChanged'));
        }

        // -------------------------------
        // UPDATE FORMSET INDICES
        // -------------------------------
        function updateFormIndices() {
            const previewItems = previewList.querySelectorAll(".preview-item");
            formCount = 0;

            previewItems.forEach((item, index) => {
                item.dataset.formIndex = index;

                const hiddenInputs = item.querySelectorAll("input[type='hidden']");
                hiddenInputs.forEach(input => {
                    const parts = input.name.split('-');
                    if (parts.length >= 3) {
                        parts[1] = index;
                        input.name = parts.join('-');
                    }
                });

                formCount++;
            });

            updateTotalForms();
        }

        // -------------------------------
        // REMOVE EXISTING ITEMS
        // -------------------------------
        previewList.addEventListener("click", function (e) {
            if (e.target.classList.contains("remove-btn") || e.target.closest(".remove-btn")) {
                const previewItem = e.target.closest(".preview-item");
                const idInput = previewItem.querySelector("input[name$='-id']");

                if (idInput && idInput.value) {
                    let deleteInput = previewItem.querySelector("input[name$='-DELETE']");
                    if (!deleteInput) {
                        deleteInput = document.createElement("input");
                        deleteInput.type = "hidden";
                        deleteInput.name = idInput.name.replace('-id', '-DELETE');
                        previewItem.appendChild(deleteInput);
                    }
                    deleteInput.value = "on";
                    previewItem.style.display = "none";
                    
                    // Notify progress bar of formset change
                    document.dispatchEvent(new CustomEvent('formsetItemChanged'));
                } else {
                    previewItem.remove();
                    updateFormIndices();
                    
                    // Notify progress bar of formset change
                    document.dispatchEvent(new CustomEvent('formsetItemChanged'));
                }
            }
        });

        // -------------------------------
        // BUTTON & ENTER KEY ADD
        // -------------------------------
        addButton.addEventListener("click", addToPreview);

        formGrid.addEventListener("keydown", (e) => {
            if (e.key === "Enter") {
                e.preventDefault();
                addToPreview();
            }
        });
    });
});