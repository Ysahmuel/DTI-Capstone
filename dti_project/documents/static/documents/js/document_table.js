document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".document-value-row").forEach(row => {
        row.addEventListener("click", () => {
            window.location = row.dataset.href;
        });
    });
});