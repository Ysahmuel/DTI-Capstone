document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('add-staff-form');
    const birthdayInput = document.getElementById('id_birthday');

    // Set max birthday to 15 years ago
    if (birthdayInput) {
        const today = new Date();
        today.setFullYear(today.getFullYear() - 15); // 15 years ago
        birthdayInput.max = today.toISOString().split('T')[0];
    }

    form.addEventListener('submit', function (e) {
        const requiredFields = ['id_first_name', 'id_last_name', 'id_default_address', 'id_default_phone', 'id_birthday'];
        let valid = true;

        requiredFields.forEach(id => {
            const input = document.getElementById(id);
            if (!input || input.value.trim() === '') {
                input.style.border = '1px solid red';
                valid = false;
            } else {
                input.style.border = '';
            }
        });

        if (!valid) {
            e.preventDefault(); // stop form from submitting
            alert("Please fill in all required fields.");
        }
    });
});
