document.addEventListener('DOMContentLoaded', function() {
    console.log('Sort script loaded');
    
    // Get all sort buttons
    const sortButtons = document.querySelectorAll('.sort-btn');
    console.log('Found sort buttons:', sortButtons.length);
    
    // Add click event listener to each sort button
    sortButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            console.log('Sort button clicked');
            
            // Get the sort field from data-sort attribute
            const sortBy = this.dataset.sort;
            console.log('Sort by:', sortBy);
            
            // Get current URL and its parameters
            const currentUrl = new URL(window.location.href);
            const currentSortBy = currentUrl.searchParams.get('sort_by') || 'date'; // Default to 'date'
            const currentOrder = currentUrl.searchParams.get('order') || 'desc';
            
            console.log('Current sort_by:', currentSortBy, 'Current order:', currentOrder);
            
            // Determine new order
            let newOrder;
            if (currentSortBy === sortBy) {
                // If clicking the same column, toggle order
                newOrder = currentOrder === 'asc' ? 'desc' : 'asc';
            } else {
                // If clicking a different column, default to descending
                newOrder = 'desc';
            }
            
            console.log('New order:', newOrder);
            
            // Update URL parameters (preserves all existing filters)
            currentUrl.searchParams.set('sort_by', sortBy);
            currentUrl.searchParams.set('order', newOrder);
            
            console.log('Redirecting to:', currentUrl.toString());
            
            // Reload page with new sort parameters
            window.location.href = currentUrl.toString();
        });
        
        // Prevent event bubbling from icon clicks
        const icon = button.querySelector('i');
        if (icon) {
            icon.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                button.click();
            });
        }
    });
    
    // Optional: Add hover effect to sort buttons
    sortButtons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.opacity = '0.7';
            this.style.cursor = 'pointer';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.opacity = '1';
        });
    });
});