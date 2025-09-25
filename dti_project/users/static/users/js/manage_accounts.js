document.addEventListener('DOMContentLoaded', function() {

    // Select all checkboxes
    document.getElementById('select-all-checkbox').addEventListener('change', function() {
        const checked = this.checked;
        document.querySelectorAll('input[name="staffs"]').forEach(cb => {
            cb.checked = checked;
        });
    });

    const userRows = document.querySelectorAll('.user-value-row');

    // Select all checkboxes
    document.getElementById('select-all-checkbox').addEventListener('change', function() {
        const checked = this.checked;
        const checkboxUserType = this.getAttribute('name')

        document.querySelectorAll('input[type="checkbox"][name]').forEach(cb => {
            cb.checked = checked;
        });
    })

})