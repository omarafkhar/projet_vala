from database import engine
from models import Base, Message

print("Creating messages table in the database...")
# This will create tables that don't exist yet, preserving exiting ones.
Base.metadata.create_all(bind=engine, tables=[Message.__table__])
print("Done!")
