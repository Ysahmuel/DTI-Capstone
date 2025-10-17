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
});
