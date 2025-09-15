document.addEventListener('DOMContentLoaded', function() {
    const bellIcon = document.querySelector('.header-notifications .fa-bell');
    const notificationsContainer = document.querySelector('.notifications-container');
    const suggestionsBox = document.getElementById('suggestions-box');
    const notificationsHeader = document.querySelector('.notifications-header');
    const notificationsList = document.querySelector('.notifications-list');

    if (bellIcon && notificationsContainer) {
        bellIcon.addEventListener('click', () => {
            notificationsContainer.classList.toggle('visible');

            if (suggestionsBox.classList.contains('visible')) {
                suggestionsBox.classList.remove('visible')
            }
        });
    }

    // automatically hide notifications list if search suggestion box is visible
    if (suggestionsBox) {
        const observer = new MutationObserver(() => {
            if (suggestionsBox.style.visibility === 'visible') {
                notificationsContainer.classList.remove('visible');
            }
        });

        observer.observe(suggestionsBox, { attributes: true, attributeFilter: ['style'] });
    }

    // click outside -> remove visibility
    document.addEventListener('click', function(e) {
        if (!bellIcon.contains(e.target) && !notificationsContainer.contains(e.target)) {
            notificationsContainer.classList.remove('visible');
        }
    });

    // --- NEW: WebSocket connection ---
    const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
    const socketUrl = protocol + window.location.host + '/ws/notifications/';
    const notificationSocket = new WebSocket(socketUrl);

    notificationSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);

        // Build new notification item
        const li = document.createElement("li");
        li.innerHTML = `
            <div class="system-icon">
                <i class="fa-solid fa-cog"></i>
            </div>
            <div class="details">
                <div class="row">${data.message}</div>
                <p class="time-since">Just now</p>
            </div>
        `;

        // Prepend it to the notifications list
        if (notificationsList) {
            notificationsList.prepend(li);
        }

        // Update bell counter
        if (bellIcon) {
            let count = parseInt(bellIcon.dataset.count || "0", 10);
            count++;
            bellIcon.dataset.count = count;
            bellIcon.setAttribute("data-count", count);
        }
    }

    notificationSocket.onclose = function(e) {
        console.error("Notification socket closed unexpectedly");
    };

})