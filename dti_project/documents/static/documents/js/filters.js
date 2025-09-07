document.addEventListener('DOMContentLoaded', function() {
    const additionalFiltersBtn = document.getElementById('filter-btn');
    const filterModalContainer = document.getElementById('document-list-filters-container');
    const closeFilterModalBtn = document.querySelector('.close-modal-btn');
    
    if (additionalFiltersBtn && filterModalContainer && closeFilterModalBtn) {
        additionalFiltersBtn.addEventListener('click', function() {
            filterModalContainer.style.display = 'flex';
        });

        closeFilterModalBtn.addEventListener('click', function() {
            filterModalContainer.style.display = 'none';
        });
    }

    const statusFilterItems = document.querySelectorAll('.status-filter-item');

    statusFilterItems.forEach(item => {
        item.addEventListener('click', function(e) {
            if (e.target.tagName.toLowerCase() === 'input') return;

            const checkbox = item.querySelector('input[type="checkbox"]');
            checkbox.checked = !checkbox.checked;

            // add or remove "active" class for styling
            item.classList.toggle('active', checkbox.checked);
        });
    });

    // initialize checked styling on page load
    statusFilterItems.forEach(item => {
        const checkbox = item.querySelector('input[type="checkbox"]');
        if (checkbox.checked) {
            item.classList.add('active');
        }
    });
});
