document.addEventListener('DOMContentLoaded', function() {
    const searchBarContainer = document.querySelector('.searchbar-container');

    searchBarContainer.addEventListener('click', function() {
        searchBarContainer.classList.add('active')
    })

    const searchInput = document.querySelector('input[name="query"]');
    const suggestionsBox = document.getElementById('suggestions-box');

    if (searchInput && suggestionsBox) {
        searchInput.addEventListener('input', function() {
            const query = this.value;
            if (query.length > 0) {
                fetch(`/search-suggestions/?query=${query}`)
                .then(response => response.json())
                .then(data => {
                    suggestionsBox.innerHTML = '';

                    // Create category header for users
                    createCategoryHeader("Users", data.user_count)

                    // Create suggestion items for matched users
                    data.users.forEach(user => {
                        const userSuggestion = createSuggestionItem("user", user)
                        suggestionsBox.append(userSuggestion)
                    })

                    // Create category header for sales promos
                    createCategoryHeader("Sales Promo Permit Applications", data.sales_promo_count)

                    data.sales_promos.forEach(promo => {
                        const salesPromoSuggestion = createSuggestionItem("salesPromo", promo)
                        suggestionsBox.append(salesPromoSuggestion)
                    })
                })

                suggestionsBox.style.visibility = 'visible';
            } else {
                suggestionsBox.style.visibility = 'hidden';
            }
        })
    }

    function createCategoryHeader(category, itemCount, filter = null, query = null) {
        const header = document.createElement('div');
        header.classList.add('suggestions-header');

        header.innerHTML = `
            <div class="suggestions-header" style="display:flex; align-items:center; justify-content: space-between; border-bottom: solid 1px var(--border-color); padding-bottom: 0.5rem;">
                <h3>${category} <span class="suggestion-count">${itemCount}</span></h3>
                <i class="fa-solid fa-angle-right"></i>
            </div>
        `
        suggestionsBox.append(header)
    }

    function createSuggestionItem(type, item) {
        const suggestionDiv = document.createElement('div');
        suggestionDiv.classList.add('suggestion-item');

        let itemContent = '';

        if (type === 'user') {
            itemContent = `
                <a href="">
                    <div class="details">
                        <div class="suggestion-item-image">
                            <img src=${item.profile_picture}></img>
                        </div>
                        <strong>${item.full_name}</strong>
                    </div>
                </a>
            `
        } else if (type === 'salesPromo') {
            itemContent = `
                <a href="">
                    <div class="details">
                        <div class="suggestion-item-image">
                            <i class="fa-solid fa-file"></i>
                        </div>
                        <strong>${item.title}</strong>
                    </div>
                </a>
            `
        }

        suggestionDiv.innerHTML = itemContent;
        return suggestionDiv;
    }
})