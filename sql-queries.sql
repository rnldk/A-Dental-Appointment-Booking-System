CREATE DATABASE dental_booking;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'dentist', 'patient') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE appointments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    dentist_id INT NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    status ENUM('booked', 'approved', 'cancelled') DEFAULT 'booked',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (patient_id) REFERENCES users(id),
    FOREIGN KEY (dentist_id) REFERENCES users(id)
);


CREATE TABLE notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    appointment_id INT NOT NULL,
    type ENUM('approved', 'cancelled') NOT NULL,
    dentist_name VARCHAR(255) NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES users(id),
    FOREIGN KEY (appointment_id) REFERENCES appointments(id)
);


CREATE TABLE reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dentist_id INT NOT NULL,
    patient_id INT NOT NULL,
    service VARCHAR(100) NOT NULL,
    appointment_status ENUM('Completed', 'No-show') NOT NULL,
    details TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dentist_id) REFERENCES users(id),
    FOREIGN KEY (patient_id) REFERENCES users(id)
);
