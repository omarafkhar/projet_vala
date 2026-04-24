INSERT INTO employees (nom, prenom, email, password, role)
SELECT 'Admin', 'User', 'admin@vala.com', '$2b$12$yfg4BNzprrlFi4LLZrmNCeT6iIIIrE7IWp/hv3eqIHWxevv2JqLt.', 'admin'
FROM DUAL
WHERE NOT EXISTS (
    SELECT 1 FROM employees WHERE email = 'admin@vala.com'
);
