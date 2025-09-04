document.addEventListener('DOMContentLoaded', function() {
    const additionalFiltersBtn = document.getElementById('filter-btn');
    const filterModalContainer = document.querySelector('.document-list-filters-container');
    const closeFilterModalBtn = document.getElementById('close-list-filters-modal-btn');
    
    additionalFiltersBtn.addEventListener('click', function() {
        filterModalContainer.style.display = 'flex'
    })

    closeFilterModalBtn.addEventListener('click', function() {
        filterModalContainer.style.display = 'none';
    })
})