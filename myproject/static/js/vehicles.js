    function filterVehicles(type) {
        const cards = document.querySelectorAll(".vehicle-card");
        cards.forEach(card => {
            if (type === 'all' || card.getAttribute("data-type") === type) {
                card.style.display = "block";
            } else { 
                card.style.display = "none";
            }
        });
    }

    function goBack() {
        window.location.href = "index.html"; // Change if your main page has a different file name
    }

    // Simulate Redirection from Main Page
    const urlParams = new URLSearchParams(window.location.search);
    const filter = urlParams.get('filter');
    if (filter) {
        filterVehicles(filter);
    }