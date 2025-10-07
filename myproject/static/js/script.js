        const showLogin = document.getElementById("showLogin");
        const showRegister = document.getElementById("showRegister");
        const loginModal = document.getElementById("loginModal");
        const registerModal = document.getElementById("registerModal");
        const closeLoginModal = document.getElementById("closeLoginModal");
        const closeRegisterModal = document.getElementById("closeRegisterModal");
        const switchToRegister = document.getElementById("switchToRegister");
        const switchToLogin = document.getElementById("switchToLogin");
        const formTabs = document.querySelectorAll(".form-tab");
        const tabContents = document.querySelectorAll(".tab-content");

        showLogin.addEventListener("click", () => loginModal.classList.add("active"));
        showRegister.addEventListener("click", () => registerModal.classList.add("active"));
        closeLoginModal.addEventListener("click", () => loginModal.classList.remove("active"));
        closeRegisterModal.addEventListener("click", () => registerModal.classList.remove("active"));
        switchToRegister.addEventListener("click", e => { e.preventDefault(); loginModal.classList.remove("active"); registerModal.classList.add("active"); });
        switchToLogin.addEventListener("click", e => { e.preventDefault(); registerModal.classList.remove("active"); loginModal.classList.add("active"); });

        formTabs.forEach(tab => {
            tab.addEventListener("click", () => {
                formTabs.forEach(t => t.classList.remove("active"));
                tabContents.forEach(content => content.classList.remove("active"));
                tab.classList.add("active");
                document.getElementById(tab.dataset.tab).classList.add("active");
            });
        });

        // Helper function to get CSRF token from cookies
        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        };