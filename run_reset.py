"""
Run this script to rebuild the database and seed users with plain-text passwords.
Usage:  python run_reset.py
"""
from sqlalchemy import create_engine, text

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:@localhost/gestion_employes"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

sql_statements = [
    "SET FOREIGN_KEY_CHECKS = 0",
    "DROP TABLE IF EXISTS presence",
    "DROP TABLE IF EXISTS conges",
    "DROP TABLE IF EXISTS tasks",
    "DROP TABLE IF EXISTS employees",
    "SET FOREIGN_KEY_CHECKS = 1",
    """
    CREATE TABLE employees (
        id       INT AUTO_INCREMENT PRIMARY KEY,
        nom      VARCHAR(100) NOT NULL,
        prenom   VARCHAR(100) NOT NULL,
        email    VARCHAR(150) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        role     VARCHAR(50)  NOT NULL DEFAULT 'employee'
    )
    """,
    """
    CREATE TABLE tasks (
        id          INT AUTO_INCREMENT PRIMARY KEY,
        employee_id INT NOT NULL,
        titre       VARCHAR(200) NOT NULL,
        description TEXT,
        deadline    DATE,
        statut      VARCHAR(50),
        FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE conges (
        id          INT AUTO_INCREMENT PRIMARY KEY,
        employee_id INT NOT NULL,
        date_debut  DATE NOT NULL,
        date_fin    DATE NOT NULL,
        reason      TEXT,
        statut      VARCHAR(50),
        FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE presence (
        id           INT AUTO_INCREMENT PRIMARY KEY,
        employee_id  INT NOT NULL,
        date         DATE NOT NULL,
        heure_entree TIME,
        heure_sortie TIME,
        statut       VARCHAR(50),
        FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
    )
    """,
    """
    INSERT INTO employees (nom, prenom, email, password, role) VALUES
        ('Admin',    'Vala',  'admin@vala.com',     '12345', 'admin'),
        ('Employee', 'One',   'employee1@vala.com', '12345', 'employee'),
        ('Employee', 'Two',   'employee2@vala.com', '12345', 'employee')
    """
]

with engine.connect() as conn:
    for stmt in sql_statements:
        try:
            conn.execute(text(stmt))
            conn.commit()
        except Exception as e:
            print(f"  [ERROR] {e}")

    # Verify
    result = conn.execute(text("SELECT id, nom, prenom, email, role FROM employees"))
    rows = result.fetchall()

print("\n=== Database Reset Complete ===")
print(f"{'ID':<5} {'Nom':<12} {'Prenom':<12} {'Email':<25} {'Role'}")
print("-" * 65)
for row in rows:
    print(f"{row[0]:<5} {row[1]:<12} {row[2]:<12} {row[3]:<25} {row[4]}")
print("\n✅ Users seeded with plain-text password: 12345")
print("✅ Login endpoint now uses direct string comparison")
print("\nTest credentials:")
print("  admin@vala.com     / 12345  (admin)")
print("  employee1@vala.com / 12345  (employee)")
print("  employee2@vala.com / 12345  (employee)")
