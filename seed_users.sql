USE gestion_employes;

-- Clean existing data
DELETE FROM employees;

-- Seed Admin
INSERT INTO employees (nom, prenom, email, password, role)
VALUES ('Admin', 'Vala', 'admin@vala.com', '$2b$12$HGTj/OuQmvMkGREuQ2vLcO4rpB/daMoE2.yOA7Pgz.CyrNAxemurq', 'admin');

-- Seed Employee 1
INSERT INTO employees (nom, prenom, email, password, role)
VALUES ('John', 'Doe', 'employee1@vala.com', '$2b$12$ZpqHqeTSK4SuAuQ9Fktc3uA047gKt08AWudwgKKqFjhBUiQllIPKa', 'employee');

-- Seed Employee 2
INSERT INTO employees (nom, prenom, email, password, role)
VALUES ('Jane', 'Smith', 'employee2@vala.com', '$2b$12$ZpqHqeTSK4SuAuQ9Fktc3uA047gKt08AWudwgKKqFjhBUiQllIPKa', 'employee');