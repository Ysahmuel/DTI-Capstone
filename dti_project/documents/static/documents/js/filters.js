document.addEventListener('DOMContentLoaded', function() {
    const additionalFiltersBtn = document.getElementById('filter-btn');
    const modalContainer = document.querySelector('.modal-container');
    const closemodalBtn = document.querySelector('.close-modal-btn');
    const clearBtn = document.getElementById('clear-btn');
    const form = document.getElementById('document-filters-form');

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
            item.classList.toggle('active', checkbox.checked);
        });

        // initialize checked styling on page load
        const checkbox = item.querySelector('input[type="checkbox"]');
        if (checkbox.checked) item.classList.add('active');
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

    // RESET button handling
    if (clearBtn && form) {
        clearBtn.addEventListener('click', function() {
            // Reset text inputs
            form.querySelectorAll('input[type="text"], input[type="date"], input[type="number"]').forEach(input => {
                input.value = '';
            });

            // Reset checkboxes
            checkboxFilterItems.forEach(item => {
                const checkbox = item.querySelector('input[type="checkbox"]');
                checkbox.checked = false;
                item.classList.remove('active');
            });

            // Reset radios to default (first radio in each group, usually "All")
            const radioGroups = {};
            radioFilterItems.forEach(item => {
                const radio = item.querySelector('input[type="radio"]');
                if (!radioGroups[radio.name]) radioGroups[radio.name] = [];
                radioGroups[radio.name].push(radio);
            });

            Object.values(radioGroups).forEach(group => {
                group.forEach((radio, idx) => {
                    if (idx === 0) {
                        radio.checked = true;
                        radio.closest('.radio-filter-item').classList.add('active');
                    } else {
                        radio.checked = false;
                        radio.closest('.radio-filter-item').classList.remove('active');
                    }
                });
            });
        });
    }
});
