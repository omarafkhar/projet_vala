from database import SessionLocal, engine
import models

def test():
    db = SessionLocal()
    try:
        user = db.query(models.Employee).first()
        if user:
            print("Connected! User:", user.email)
        else:
            print("Connected but no users found.")
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test()
