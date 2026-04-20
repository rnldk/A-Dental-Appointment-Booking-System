# Dental Appointment Booking System

## Overview

This project is a web-based Dental Appointment Booking System developed for **Upper Hill Dental Centre** to improve the efficiency of appointment scheduling and patient management.

Traditional booking methods such as phone calls and emails were found to be inefficient, error-prone, and time-consuming. This system provides a digital solution that allows patients to book, reschedule, and cancel appointments online while enabling staff to manage schedules more effectively.

---

## Problem Statement

Upper Hill Dental Centre relied on manual appointment booking methods, leading to:

* Missed or double-booked appointments
* Slow response times
* Poor record management
* Reduced patient satisfaction

This system was developed to automate scheduling, reduce human error, and improve overall service delivery.

---

## Objectives

* Develop a web-based appointment booking system
* Enable patients to book, reschedule, and cancel appointments
* Allow dentists and admins to manage and approve bookings
* Improve efficiency and patient experience

---

## Features

### Patient Features

* Register and log in
* Book appointments
* Reschedule or cancel appointments
* Receive notifications on appointment status
* View appointment history

### Dentist Features

* View daily schedule
* Approve or request rescheduling of appointments
* Create and manage patient reports

### Admin Features

* Approve or cancel appointments
* Manage all system bookings
* Register dentists
* View system statistics and reports

---

## Tech Stack

* **Backend:** Flask (Python)
* **Frontend:** HTML, CSS, JavaScript
* **Database:** MySQL
* **Tools:** Git, GitHub

---

## System Architecture

The system follows a client-server architecture:

* Frontend handles user interaction
* Flask handles application logic
* MySQL manages data storage

Main modules:

* User Authentication
* Appointment Management
* Role-Based Access Control
* Database Management

---

## Database Design

### Main Tables

* **Users** – stores user credentials and roles
* **Appointments** – stores booking details
* **Notifications** – stores system alerts
* **Reports** – stores dentist reports

### Relationships

* One patient can have multiple appointments
* One dentist can handle multiple appointments

---

## Key Functionalities

* Secure user authentication with role-based access
* Real-time appointment scheduling and updates
* Prevention of double bookings
* Notification system for appointment updates
* Centralized patient record management

---

## Business Value

* Reduces administrative workload
* Improves scheduling efficiency
* Minimizes missed appointments
* Enhances patient satisfaction
* Enables better decision-making through reports

---

## Testing

The system was tested using:

* Unit Testing
* Integration Testing
* Validation Testing
* System (High-Order) Testing

Test results confirmed:

* Accurate database operations
* Correct system outputs
* Reliable performance under normal conditions

---

## Installation & Setup

1. Clone the repository:

```
git clone https://github.com/rnldk/A-Dental-Appointment-Booking-System.git
```

2. Navigate to the project folder:

```
cd A-Dental-Appointment-Booking-System
```

3. Install dependencies:

```
pip install flask mysql-connector-python
```

4. Create MySQL database:

```
dental_booking
```

5. Import the SQL file (tables: users, appointments, notifications, reports)

6. Update database connection in `app.py`

7. Run the application:

```
python app.py
```

8. Open in browser:

```
http://127.0.0.1:5000
```

---

## Usage

* Register as a patient
* Log in to access dashboard
* Book and manage appointments
* Admin and dentists manage scheduling and approvals

---

## Limitations

* No online payment integration
* No multi-clinic support
* Limited external system integration
* Basic role-based access control

---

## Future Improvements

* SMS and email notifications
* Online payment integration
* Mobile application version
* Advanced analytics dashboards
* Integration with health systems
* Enhanced security (e.g., 2FA)

---

## Conclusion

The system successfully replaces manual appointment booking with a digital solution that improves efficiency, reduces errors, and enhances patient experience. It demonstrates practical application of Flask, MySQL, and full-stack development in solving real-world healthcare challenges.

---

## Author

**Ronald Kariuki Ndirangu**
