# 🚗 Gryphon Rentals – Car and Bike Rental System

A **full-stack web application** that enables users to rent cars and bikes through a seamless, user-friendly platform. Gryphon Rentals provides real-time filtering, secure authentication, intelligent booking management, and dynamic pricing to make vehicle rentals efficient and intuitive.

## 📖 Table of Contents

1. [Introduction](#-introduction)
2. [Features](#-features)
3. [Tech Stack](#-tech-stack)
4. [Installation](#-installation)
5. [Configuration](#-configuration)
6. [Usage](#-usage)
7. [Application Flow](#-application-flow)
8. [Learning Outcomes](#-learning-outcomes)
9. [Troubleshooting](#-troubleshooting)
10. [Future Enhancements](#-future-enhancements)
11. [Contributors](#-contributors)
12. [License](#-license)

## 🔹 Introduction

**Gryphon Rentals** is a comprehensive vehicle rental system developed to simplify the process of renting cars and bikes online. It integrates real-time data handling, reservation tracking, and user management in one cohesive platform.

Users can browse, filter, and book vehicles based on preferences such as type, location, and availability. Admins have dedicated dashboards to manage users, vehicles, and bookings effectively.

## 🚀 Features

### 🧭 User-Facing

* **Responsive UI:** Clean, modern design with pages like *Home*, *About*, *Contact*, *Login/Register*.
* **Vehicle Listing & Filters:** Dynamic filters for cars and bikes that update listings instantly.
* **Smart Reservation System:** Select start/end date and location; price auto-calculates.
* **Dummy Payment Gateway:** Simulated payment logic with CVV-based success/failure validation.
* **My Reservations Dashboard:** Track active, completed, or canceled bookings; retry payments.
* **Availability Calendar:** Integrated with **Flatpickr**—disables booked dates automatically.
* **Profile Dashboard:** Displays user info, rental stats, preferred vehicle type, and total spend.

### 🔧 Admin Panel

* Manage **users**, **reservations**, and **vehicle inventory**.
* Filter bookings by status (success, failure, pending).
* Add or remove vehicles dynamically.
* View **session logs** and system insights.

### 🌐 Additional Features

* **Pagination** for vehicle listings.
* **Footer Navigation:** Quick access to legal and info pages (*About*, *Privacy Policy*, *Terms of Service*, etc.).


## 🧰 Tech Stack

| Layer              | Technology                                                         |
| ------------------ | ------------------------------------------------------------------ |
| **Frontend**       | HTML5, CSS3, JavaScript, Bootstrap, Flatpickr                      |
| **Backend**        | Python, Django, Django REST Framework                              |
| **Database**       | SQLite (via DB Browser)                                            |
| **Authentication** | Django Auth                                                        |
| **Tools**          | VS Code, GitHub, Django Admin, Firebase *(for future integration)* |


## ⚙️ Installation

### Prerequisites

* Python 3.8+
* pip (Python package manager)
* Git

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/gryphon-rentals.git

# 2. Navigate to project directory
cd gryphon-rentals

# 3. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # For Linux/macOS
venv\Scripts\activate      # For Windows

# 4. Install dependencies
pip install -r requirements.txt

# 5. Apply migrations
python manage.py migrate

# 6. Run the development server
python manage.py runserver

Now open **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)** in your browser to access Gryphon Rentals.


## ⚙️ Configuration

* **Environment Variables (optional)**
  Create a `.env` file in the root directory and configure:


  SECRET_KEY=your_secret_key
  DEBUG=True
  ALLOWED_HOSTS=127.0.0.1,localhost
  
* **Admin Access**

  ```bash
  python manage.py createsuperuser
  ```

  Use this to manage vehicles, users, and bookings via Django Admin.


## 💻 Usage

1. Register or log in using email or phone.
2. Browse available vehicles (cars/bikes).
3. Apply filters (type, price, location).
4. Select rental dates and confirm booking.
5. Proceed to payment (dummy gateway for demo).
6. View your reservation status under “My Reservations”.
7. Admins can log in to manage data through the Admin Panel.


## 🔄 Application Flow

```text
User → Browse → Filter Vehicles → Select Dates → Reserve → Payment → Dashboard → Admin Management
```


## 📘 Learning Outcomes

This project provided hands-on experience with:

* Frontend-backend integration
* Dynamic rendering & state management
* Role-based authentication
* Model and admin panel customization
* Pagination & real-time calendar logic
* Clean and secure user experience design


## 🧩 Troubleshooting

| Issue                    | Solution                                                         |
| ------------------------ | ---------------------------------------------------------------- |
| Database errors          | Run `python manage.py migrate` again.                            |
| Static files not loading | Use `python manage.py collectstatic`.                            |
| Calendar not displaying  | Ensure Flatpickr JS and CSS are properly linked in the template. |
| Payment page not working | Check dummy payment validation logic and routes.                 |


## 🌱 Future Enhancements

* Integration with **real payment gateways** (Stripe/PayPal)
* **Firebase authentication** and notifications
* **Mobile app companion** (React Native)
* **Enhanced analytics dashboard** for admins


## 👥 Contributors

* **[Your Name](https://github.com/<your-username>)** – Full-Stack Developer & Project Creator
* Contributions welcome! Fork this repo and open a pull request to suggest improvements.

## 📜 License

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

