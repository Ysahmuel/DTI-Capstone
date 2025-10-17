document.addEventListener('DOMContentLoaded', function() {
    const additionalFiltersBtn = document.getElementById('filter-btn');
    const modalContainer = document.querySelector('.modal-container');
    const closemodalBtn = document.querySelector('.close-modal-btn');
    
    if (additionalFiltersBtn && modalContainer && closemodalBtn) {
        additionalFiltersBtn.addEventListener('click', function() {
            modalContainer.style.display = 'flex';
        });
    }

    if (modalContainer && closemodalBtn) {
        closemodalBtn.addEventListener('click', function() {
            modalContainer.style.display = 'none';
        });
    }

    // Checkbox handling
    const checkboxFilterItems = document.querySelectorAll('.checkbox-filter-item');

    checkboxFilterItems.forEach(item => {
        item.addEventListener('click', function(e) {
            if (e.target.tagName.toLowerCase() === 'input') return;

            const checkbox = item.querySelector('input[type="checkbox"]');
            checkbox.checked = !checkbox.checked;

            // add or remove "active" class for styling
            item.classList.toggle('active', checkbox.checked);
        });
    });

    // initialize checked styling on page load
    checkboxFilterItems.forEach(item => {
        const checkbox = item.querySelector('input[type="checkbox"]');
        if (checkbox.checked) {
            item.classList.add('active');
        }
    });

    // Radio handling
    const radioFilterItems = document.querySelectorAll('.radio-filter-item');

    radioFilterItems.forEach(item => {
        const radio = item.querySelector('input[type="radio"]');

        // style the initially checked radio
        if (radio.checked) item.classList.add('active');

        item.addEventListener('click', function(e) {
            if (e.target.tagName.toLowerCase() === 'input') return;

            // uncheck all radios in the same group
            const name = radio.name;
            document.querySelectorAll(`input[name="${name}"]`).forEach(r => {
                r.checked = false;
                r.closest('.radio-filter-item').classList.remove('active');
            });

            // check the clicked one
            radio.checked = true;
            item.classList.add('active');
        });

        // also handle clicking the radio itself
        radio.addEventListener('change', function() {
            if (radio.checked) {
                document.querySelectorAll(`input[name="${radio.name}"]`).forEach(r => {
                    if (r !== radio) r.closest('.radio-filter-item').classList.remove('active');
                });
                item.classList.add('active');
            }
        });
    });
});
