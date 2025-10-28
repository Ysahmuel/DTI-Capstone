document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('profile-edit-form');
    const birthdayInput = document.getElementById('id_birthday');

    // Set max birthday to 15 years ago (prevent minors)
    if (birthdayInput) {
        const today = new Date();
        today.setFullYear(today.getFullYear() - 15);
        birthdayInput.max = today.toISOString().split('T')[0];
    }

    // Validate required fields before submitting
    if (form) {
        form.addEventListener('submit', function (e) {
            const requiredFields = [
                'id_first_name',
                'id_last_name',
                'id_email',
                'id_default_address',
                'id_default_phone',
                'id_birthday'
            ];

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
                e.preventDefault();
                alert("Please fill in all required fields.");
            }
        });
    }

    // Toast notification for successful save (green popup bottom-right)
    const toast = document.createElement('div');
    toast.id = 'profile-toast';
    toast.style.position = 'fixed';
    toast.style.bottom = '20px';
    toast.style.right = '20px';
    toast.style.backgroundColor = '#28a745';
    toast.style.color = '#fff';
    toast.style.padding = '12px 20px';
    toast.style.borderRadius = '8px';
    toast.style.boxShadow = '0 2px 6px rgba(0,0,0,0.2)';
    toast.style.opacity = '0';
    toast.style.transition = 'opacity 0.3s ease';
    toast.style.zIndex = '9999';
    toast.textContent = 'Profile updated successfully!';
    document.body.appendChild(toast);

    // Show toast if redirected after saving
    const params = new URLSearchParams(window.location.search);
    if (params.get('updated') === 'true') {
        toast.style.opacity = '1';
        setTimeout(() => toast.style.opacity = '0', 3000);
    }
});
