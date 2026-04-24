-- ============================================================
-- VALA HR SYSTEM - CLEAN DATABASE RESET
-- Run this in MySQL Workbench or: mysql -u root gestion_employes < reset_db.sql
-- ============================================================

USE gestion_employes;

-- 1. Drop dependent tables first (foreign keys)
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS presence;
DROP TABLE IF EXISTS conges;
DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS employees;
SET FOREIGN_KEY_CHECKS = 1;

-- 2. Recreate employees table
CREATE TABLE employees (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    nom      VARCHAR(100) NOT NULL,
    prenom   VARCHAR(100) NOT NULL,
    email    VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role     VARCHAR(50)  NOT NULL DEFAULT 'employee'
);

-- 3. Recreate tasks table
CREATE TABLE tasks (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    titre       VARCHAR(200) NOT NULL,
    description TEXT,
    deadline    DATE,
    statut      VARCHAR(50),
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
);

-- 4. Recreate conges table
CREATE TABLE conges (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    date_debut  DATE NOT NULL,
    date_fin    DATE NOT NULL,
    reason      TEXT,
    statut      VARCHAR(50),
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
);

-- 5. Recreate presence table
CREATE TABLE presence (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    employee_id  INT NOT NULL,
    date         DATE NOT NULL,
    heure_entree TIME,
    heure_sortie TIME,
    statut       VARCHAR(50),
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
);

-- 6. Insert users with PLAIN TEXT passwords (login will compare directly)
INSERT INTO employees (nom, prenom, email, password, role) VALUES
    ('Admin',    'Vala',  'admin@vala.com',     '12345', 'admin'),
    ('Employee', 'One',   'employee1@vala.com', '12345', 'employee'),
    ('Employee', 'Two',   'employee2@vala.com', '12345', 'employee');

-- 7. Confirm
SELECT id, nom, prenom, email, role FROM employees;
