CREATE DATABASE IF NOT EXISTS gestion_employes;
USE gestion_employes;

-- Drop existing tables to start fresh
DROP TABLE IF EXISTS presence;
DROP TABLE IF EXISTS conges;
DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS employees;

-- Recreate employees table with requested columns
CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'employee'
);

-- Recreate other tables for a complete setup (if still needed)
CREATE TABLE tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT,
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    deadline DATE,
    statut VARCHAR(50),
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
);

CREATE TABLE conges (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT,
    date_debut DATE NOT NULL,
    date_fin DATE NOT NULL,
    reason TEXT,
    statut VARCHAR(50),
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
);

CREATE TABLE presence (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT,
    date DATE NOT NULL,
    heure_entree TIME,
    heure_sortie TIME,
    statut VARCHAR(50),
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
);

CREATE TABLE messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender_id INT,
    receiver_id INT,
    content TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_read BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (sender_id) REFERENCES employees(id) ON DELETE CASCADE,
    FOREIGN KEY (receiver_id) REFERENCES employees(id) ON DELETE CASCADE
);
