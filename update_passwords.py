from database import SessionLocal
from models import Employee
from main import get_password_hash

def update_all_passwords():
    session = SessionLocal()
    try:
        # Generate the hashed password for "12345"
        hashed_password = get_password_hash("12345")
        print(f"Generated hashed password: {hashed_password}")
        
        # Get all employees
        employees = session.query(Employee).all()
        
        count = 0
        for employee in employees:
            employee.password = hashed_password
            count += 1
            
        # Commit the changes
        session.commit()
        print(f"Successfully updated passwords for {count} users.")
    except Exception as e:
        session.rollback()
        print(f"An error occurred: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    update_all_passwords()
