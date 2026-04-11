CREATE DATABASE IF NOT EXISTS gestion_employes;
USE gestion_employes;

CREATE TABLE IF NOT EXISTS employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    telephone VARCHAR(20),
    poste VARCHAR(100),
    departement VARCHAR(100),
    date_embauche DATE,
    statut VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT,
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    deadline DATE,
    statut VARCHAR(50),
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS conges (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT,
    date_debut DATE NOT NULL,
    date_fin DATE NOT NULL,
    statut VARCHAR(50),
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS presence (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT,
    date DATE NOT NULL,
    heure_entree TIME,
    heure_sortie TIME,
    statut VARCHAR(50),
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
);
