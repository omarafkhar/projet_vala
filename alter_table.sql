-- Migration: Add department and status columns to employees table
-- Run this once against your HR database

ALTER TABLE employees
    ADD COLUMN IF NOT EXISTS department VARCHAR(100) NULL,
    ADD COLUMN IF NOT EXISTS status VARCHAR(50) NOT NULL DEFAULT 'active';

-- Optional: seed some departments for existing employees
UPDATE employees SET department = 'Engineering' WHERE department IS NULL AND role = 'employee' LIMIT 2;
UPDATE employees SET department = 'HR' WHERE department IS NULL AND role = 'admin' LIMIT 1;
UPDATE employees SET department = 'Operations' WHERE department IS NULL LIMIT 5;
UPDATE employees SET department = 'Marketing' WHERE department IS NULL;
