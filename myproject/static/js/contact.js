    const contactBtn = document.getElementById("contactBtn");
    const contactPopup = document.getElementById("contactPopup");
    const closeBtn = document.getElementById("closeBtn");
 
    // Show popup with animation
    contactBtn.onclick = function() {
        contactPopup.style.display = "block";
    }

    // Close popup and redirect to main page
    closeBtn.onclick = function() {
        window.location.href = "index.html";  // Change to your actual main page file name if different
    }

    // Close popup if user clicks outside the content
    window.onclick = function(event) {
        if (event.target === contactPopup) {
            contactPopup.style.display = "none";
        }
    }