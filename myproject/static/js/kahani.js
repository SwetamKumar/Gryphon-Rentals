        // DOM Elements
        const vehicleGrid = document.getElementById('vehicleGrid');
        const reservationsList = document.getElementById('reservationsList');
        const navItems = document.querySelectorAll('.nav-item');
        const sections = document.querySelectorAll('.section');
        const filterBtns = document.querySelectorAll('.filter-btn');
        const rentalModal = document.getElementById('rentalModal');
        const closeBtn = document.querySelector('.close-btn');
        const cancelRentalBtn = document.getElementById('cancelRental');
        const rentalForm = document.getElementById('rentalForm');
        const pickupDateInput = document.getElementById('pickupDate');
        const returnDateInput = document.getElementById('returnDate');
        const summaryVehicle = document.getElementById('summaryVehicle');
        const summaryDuration = document.getElementById('summaryDuration');
        const summaryRate = document.getElementById('summaryRate');
        const summaryTotal = document.getElementById('summaryTotal');
        const reservationSection = document.getElementById("reservationSection");

        // Current state
        let selectedVehicle = null;
        let activeFilter = 'all';
        let currentPage = 1;
        let pickupDatepicker = null;
        let returnDatepicker = null;
        let searchTimer = null; // For debouncing search input

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            loadVehicles();
            setMinDates();
        });

        // Navigation
        navItems.forEach(item => {
            item.addEventListener('click', function() {
                const targetSectionId = this.getAttribute('data-section');
                
                // Update nav items
                navItems.forEach(navItem => navItem.classList.remove('active'));
                this.classList.add('active');
                
                // Update sections
                sections.forEach(section => {
                    if (section.id === targetSectionId) {
                        section.classList.add('active');
                    } else {
                        section.classList.remove('active');
                    }
                });
            });
        });

        // Filters
        filterBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const filter = this.getAttribute('data-filter');
                activeFilter = filter;
                
                // Update buttons
                filterBtns.forEach(filterBtn => filterBtn.classList.remove('active'));
                this.classList.add('active');
                
                // Filter vehicles
                loadVehicles();
            });
        });

        // Load vehicles based on filter
        async function loadVehicles() {
            const searchQuery = document.getElementById('searchInput').value;
            try {
                // Build the URL with query parameters for pagination, filtering, and search
                const url = `/api/vehicles/?page=${currentPage}&filter=${activeFilter}&search=${searchQuery}`;
                const response = await fetch(url);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();

                vehicleGrid.innerHTML = '';
                
                if (data.vehicles && data.vehicles.length > 0) {
                    data.vehicles.forEach(vehicle => {
                        const vehicleCard = createVehicleCard(vehicle);
                        vehicleGrid.appendChild(vehicleCard);
                    });
                } else {
                    vehicleGrid.innerHTML = '<p class="error-message">No vehicles found.</p>';
                }

                // Render the pagination controls based on the response data
                renderPagination(data);

            } catch (error) {
                console.error("Could not load vehicles:", error);
                vehicleGrid.innerHTML = '<p class="error-message">Could not load vehicles. Please try again later.</p>';
            }
        }

        // Create and manage pagination controls
        function renderPagination(data) {
            const paginationControls = document.getElementById('paginationControls');
            if (!paginationControls) return;

            paginationControls.innerHTML = ''; // Clear old controls

            // Don't show controls if there's only one page or no results
            if (data.total_pages <= 1) {
                return;
            }

            // Previous Button
            const prevBtn = document.createElement('button');
            prevBtn.textContent = 'Previous';
            prevBtn.className = 'pagination-btn';
            prevBtn.disabled = !data.has_previous;
            prevBtn.addEventListener('click', () => {
                if (data.has_previous) {
                    currentPage--;
                    loadVehicles();
                }
            });

            // Page Info Text
            const pageInfo = document.createElement('span');
            pageInfo.className = 'page-info';
            pageInfo.textContent = `Page ${data.current_page} of ${data.total_pages}`;

            // Next Button
            const nextBtn = document.createElement('button');
            nextBtn.textContent = 'Next';
            nextBtn.className = 'pagination-btn';
            nextBtn.disabled = !data.has_next;
            nextBtn.addEventListener('click', () => {
                if (data.has_next) {
                    currentPage++;
                    loadVehicles();
                }
            });

            paginationControls.appendChild(prevBtn);
            paginationControls.appendChild(pageInfo);
            paginationControls.appendChild(nextBtn);
        }

        // Create vehicle card
        function createVehicleCard(vehicle) {
            const card = document.createElement('div');
            card.className = 'vehicle-card';

            card.innerHTML = `
                <div class="vehicle-image"><img src="${vehicle.image}" alt="${vehicle.name}"></div>
                <div class="vehicle-info">
                    <div class="vehicle-title">
                        <div class="vehicle-name">${vehicle.name}</div>
                        <div class="vehicle-price">$${vehicle.price}/${vehicle.priceUnit}</div>
                    </div>
                    <div class="vehicle-details">
                        ${vehicle.features.map(feature => `
                            <div class="vehicle-detail">
                                <span class="detail-icon">•</span>
                                <span>${feature}</span>
                            </div>
                        `).join('')}
                    </div>
                    <button class="rent-btn" data-id="${vehicle.id}">Rent Now</button>
                </div>
            `;
            
            const rentBtn = card.querySelector('.rent-btn');
            rentBtn.addEventListener('click', function() {
                openRentalModal(vehicle);
            });
            
            return card;
        }

        // Open rental modal
        async function openRentalModal(vehicle) {
            selectedVehicle = vehicle;
            summaryVehicle.textContent = vehicle.name;
            summaryRate.textContent = `${vehicle.price}/${vehicle.priceUnit}`;
            
            // Reset form
            rentalForm.reset();
            updateDuration();

            // Fetch booked dates and initialize date pickers
            try {
                const response = await fetch(`/api/vehicle/${vehicle.id}/booked-dates/`);
                const bookedDates = await response.json();

                // Destroy previous instances if they exist
                if (pickupDatepicker) pickupDatepicker.destroy();
                if (returnDatepicker) returnDatepicker.destroy();

                // Initialize flatpickr for the pickup date
                pickupDatepicker = flatpickr(pickupDateInput, {
                    minDate: "today",
                    disable: bookedDates,
                    dateFormat: "Y-m-d",
                    onChange: function(selectedDates, dateStr, instance) {
                        // When pickup date changes, update the minDate for the return date picker
                        if (returnDatepicker) {
                            const nextDay = new Date(selectedDates[0]);
                            nextDay.setDate(nextDay.getDate() + 1);
                            returnDatepicker.set('minDate', nextDay);
                        }
                    }
                });

                // Initialize flatpickr for the return date
                returnDatepicker = flatpickr(returnDateInput, {
                    minDate: new Date().fp_incr(1), // Default to tomorrow
                    disable: bookedDates,
                    dateFormat: "Y-m-d",
                });

            } catch (error) {
                console.error("Could not fetch booked dates:", error);
                setMinDates(); // Fallback to default behavior if API fails
            }
            
            // Show modal
            rentalModal.classList.add('show');
        }

        // Close rental modal
        function closeRentalModal() {
            rentalModal.classList.remove('show');
            selectedVehicle = null;
            // Destroy datepicker instances to clean up
            if (pickupDatepicker) {
                pickupDatepicker.destroy();
                pickupDatepicker = null;
            }
            if (returnDatepicker) {
                returnDatepicker.destroy();
                returnDatepicker = null;
            }
        }

        // Set minimum dates to today
        function setMinDates() {
            const today = new Date();
            const yyyy = today.getFullYear();
            const mm = String(today.getMonth() + 1).padStart(2, '0');
            const dd = String(today.getDate()).padStart(2, '0');
            const todayStr = `${yyyy}-${mm}-${dd}`;
            
            pickupDateInput.min = todayStr;
            returnDateInput.min = todayStr;
        }

        // Update duration and total when dates change
        function updateDuration() {
            const pickupDate = new Date(pickupDateInput.value);
            const returnDate = new Date(returnDateInput.value);
            
            if (isNaN(pickupDate.getTime()) || isNaN(returnDate.getTime())) {
                summaryDuration.textContent = '-';
                summaryTotal.textContent = '-';
                return;
            }
            
            // Calculate duration in days
            const timeDiff = returnDate - pickupDate;
            const days = Math.ceil(timeDiff / (1000 * 3600 * 24));
            
            if (days <= 0) {
                summaryDuration.textContent = 'Invalid dates';
                summaryTotal.textContent = '-';
                return;
            }
            
            summaryDuration.textContent = `${days} days`;
            
            if (selectedVehicle) {
                const total = selectedVehicle.price * days;
                summaryTotal.textContent = `${total}`;
            }
        }

        // Event listeners
        closeBtn.addEventListener('click', closeRentalModal);
        cancelRentalBtn.addEventListener('click', closeRentalModal);
        
        pickupDateInput.addEventListener('change', updateDuration);

        rentalForm.addEventListener('submit', async function(event) {
            event.preventDefault(); // Prevent default form submission
        
            const rentalData = {
                vehicle_id: selectedVehicle.id,
                start_date: pickupDateInput.value,
                end_date: returnDateInput.value,
                pickup_location: document.getElementById('pickupLocation').value,
            };
        
            try {
                const response = await fetch('/api/rent/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken') // Helper function to get CSRF token
                    },
                    body: JSON.stringify(rentalData)
                });
        
                const result = await response.json();
        
                if (response.ok && result.status === 'success' && result.redirect_url) {
                    // The backend confirmed the reservation is pending. Redirect to the payment page.
                    window.location.href = result.redirect_url;
                } else {
                    // If there's a server-side error (e.g., validation, conflict), show it to the user.
                    alert(`Error: ${result.message || 'An unknown error occurred.'}`);
                }
            } catch (error) {
                console.error('Error submitting reservation request:', error);
                alert('An unexpected error occurred. Please try again.');
            }
        });

        returnDateInput.addEventListener('change', updateDuration);
        
        // Add search functionality
        const searchForm = document.createElement('div');
        searchForm.className = 'search-form';
        searchForm.innerHTML = `
            <input type="text" id="searchInput" class="form-control" placeholder="Search vehicles...">
        `;
        
        document.querySelector('.vehicle-filters').insertAdjacentElement('beforebegin', searchForm);
        
        const searchInput = document.getElementById('searchInput');
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimer);
            // Use a timer to avoid sending a request on every single keystroke
            searchTimer = setTimeout(() => {
                currentPage = 1; // Reset to the first page for a new search
                loadVehicles();
            }, 300); // Wait 300ms after user stops typing
        });
        // Add style for search form
        const styleElement = document.createElement('style');
        styleElement.textContent = `
            .search-form {
                margin-bottom: 20px;
                display: flex;
                justify-content: center;
            }
            
            .search-form input {
                width: 100%;
                max-width: 400px;
                padding: 10px 15px;
                border: 1px solid #ddd;
                border-radius: 25px;
                font-size: 16px;
            }
        `;
        document.head.appendChild(styleElement);

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
        }
