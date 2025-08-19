document.addEventListener('DOMContentLoaded', function() {
    const searchBarContainer = document.querySelector('.searchbar-container');

    searchBarContainer.addEventListener('click', function() {
        searchBarContainer.classList.add('active');
    });

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
                    console.log('Response Data', data);

                    if (data.role === 'admin') {
                        // Admin: show users
                        if (data.user_count > 0) {
                            createCategoryHeader("Users", data.user_count);
                           const suggestionList = createSuggestionList()
                            data.users.forEach(user => {
                                const userSuggestion = createSuggestionItem("user", user);
                                suggestionList.append(userSuggestion);
                            });
                            suggestionsBox.append(suggestionList); 
                        }
                    }

                    // Both admin + business_owner: show documents
                    if (data.documents.count > 0) {
                        createCategoryHeader(data.role === 'admin' ? 'Documents' : 'My Documents', data.documents.count);
                        const suggestionList = createSuggestionList()
                        data.documents.results.forEach(result => {
                            const documentSuggestion = createSuggestionItem("document", result);
                            suggestionList.append(documentSuggestion);
                        });
                        suggestionsBox.append(suggestionList); 
                    }
                });

                suggestionsBox.style.visibility = 'visible';
            } else {
                suggestionsBox.style.visibility = 'hidden';
            }
        });
    }

    function createCategoryHeader(category, itemCount) {
        const header = document.createElement('div');
        header.classList.add('suggestions-header');

        header.innerHTML = `
            <div style="display:flex; align-items:center; justify-content: space-between;">
                <h3>${category} <span class="suggestion-count">${itemCount}</span></h3>
                <i class="fa-solid fa-angle-right"></i>
            </div>
        `;
        suggestionsBox.append(header);
    }

    function createSuggestionList() {
        const suggestionList = document.createElement('div');
        suggestionList.classList.add('suggestions-list');
        return suggestionList;
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
                        <span class="role">${item.role}</span>
                    </div>
                </a>
            `;
        } else if (type === 'document') {
            itemContent = `
                <a href="">
                    <div class="details">
                        <div class="suggestion-item-image">
                            <i class="fa-solid fa-file"></i>
                        </div>
                        <strong>${item.display}</strong>
                        <span class="doc-type">${item.model}</span>
                    </div>
                </a>
            `;
        }

        suggestionDiv.innerHTML = itemContent;
        return suggestionDiv;
    }
});
