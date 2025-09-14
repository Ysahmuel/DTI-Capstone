document.addEventListener('DOMContentLoaded', function() {
    const bellIcon = document.querySelector('.header-notifications .fa-bell');
    const notificationsList = document.querySelector('.notifications-container');
    const suggestionsBox = document.getElementById('suggestions-box');

    if (bellIcon && notificationsList) {
        bellIcon.addEventListener('click', () => {
            notificationsList.classList.toggle('visible');

            if (suggestionsBox.classList.contains('visible')) {
                suggestionsBox.classList.remove('visible')
            }
        });
    }

    // automatically hide notifications list if search suggestion box is visible
    if (suggestionsBox) {
        const observer = new MutationObserver(() => {
            if (suggestionsBox.style.visibility === 'visible') {
                notificationsList.classList.remove('visible');
            }
        });

        observer.observe(suggestionsBox, { attributes: true, attributeFilter: ['style'] });
    }

    // click outside -> remove visibility
    document.addEventListener('click', function(e) {
        if (!bellIcon.contains(e.target) && !notificationsList.contains(e.target)) {
            notificationsList.classList.remove('visible');
        }
    });

})