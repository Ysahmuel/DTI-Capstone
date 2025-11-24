document.addEventListener('DOMContentLoaded', function() {
    // Define the change checkbox and their corresponding from/to fields
    const changeFieldGroups = [
        {
            checkbox: 'change_territorial_scope',
            fromField: 'territorial_scope_from',
            toField: 'territorial_scope_to',
            fieldsetId: 'change-territorial-scope-fieldset'
        },
        {
            checkbox: 'change_owner_name',
            fromField: 'owner_name_from',
            toField: 'owner_name_to',
            fieldsetId: 'change-owner-name-fieldset'
        },
        {
            checkbox: 'change_business_address',
            fromField: 'business_address_from',
            toField: 'business_address_to',
            fieldsetId: 'change-business-address-fieldset'
        },
        {
            checkbox: 'change_owner_address',
            fromField: 'owner_address_from',
            toField: 'owner_address_to',
            fieldsetId: 'change-owner-address-fieldset'
        }
    ];

    // Function to check if any field in a group has value
    function hasFieldValues(fromFieldName, toFieldName) {
        const fromField = document.querySelector(`[name="${fromFieldName}"]`);
        const toField = document.querySelector(`[name="${toFieldName}"]`);
        
        const fromValue = fromField ? fromField.value.trim() : '';
        const toValue = toField ? toField.value.trim() : '';
        
        return fromValue !== '' || toValue !== '';
    }

    // Function to update checkbox and fieldset visibility
    function updateFieldsetVisibility(group) {
        const checkbox = document.querySelector(`[name="${group.checkbox}"]`);
        const fieldset = document.getElementById(group.fieldsetId);
        const fromField = document.querySelector(`[name="${group.fromField}"]`);
        const toField = document.querySelector(`[name="${group.toField}"]`);
        
        if (!checkbox || !fieldset) return;
        
        const hasValues = hasFieldValues(group.fromField, group.toField);
        
        // Auto-check checkbox if fields have values
        if (hasValues) {
            checkbox.checked = true;
            fieldset.style.display = 'block';
        } else {
            // If checkbox is manually unchecked and fields are empty, hide fieldset
            if (!checkbox.checked) {
                fieldset.style.display = 'none';
                // Clear the fields
                if (fromField) fromField.value = '';
                if (toField) toField.value = '';
            }
        }
        
        // Show fieldset when checkbox is checked
        if (checkbox.checked) {
            fieldset.style.display = 'block';
        }
    }

    // Function to update all fieldsets
    function updateAllFieldsets() {
        changeFieldGroups.forEach(group => {
            updateFieldsetVisibility(group);
        });
        
        // Update progress indicator
        updateProgressSteps();
        
        // Recalculate step completion
        if (typeof checkStepCompletion === 'function') {
            checkStepCompletion();
        }
    }

    // Function to update progress steps visibility
    function updateProgressSteps() {
        changeFieldGroups.forEach(group => {
            const checkbox = document.querySelector(`[name="${group.checkbox}"]`);
            const fieldset = document.getElementById(group.fieldsetId);
            const step = document.querySelector(`[data-target="${group.fieldsetId}"]`);
            
            if (step && fieldset) {
                if (fieldset.style.display === 'none') {
                    step.style.display = 'none';
                } else {
                    step.style.display = '';
                }
            }
        });
    }

    // Add event listeners to all checkboxes
    changeFieldGroups.forEach(group => {
        const checkbox = document.querySelector(`[name="${group.checkbox}"]`);
        
        if (checkbox) {
            checkbox.addEventListener('change', function() {
                updateFieldsetVisibility(group);
            });
        }
        
        // Add event listeners to from/to fields
        const fromField = document.querySelector(`[name="${group.fromField}"]`);
        const toField = document.querySelector(`[name="${group.toField}"]`);
        
        if (fromField) {
            fromField.addEventListener('input', () => updateFieldsetVisibility(group));
            fromField.addEventListener('change', () => updateFieldsetVisibility(group));
        }
        
        if (toField) {
            toField.addEventListener('input', () => updateFieldsetVisibility(group));
            toField.addEventListener('change', () => updateFieldsetVisibility(group));
        }
    });

    // Initialize on page load
    updateAllFieldsets();
});