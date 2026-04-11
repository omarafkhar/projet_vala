from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# User needs to install dependencies:
# pip install fastapi uvicorn sqlalchemy pymysql pydantic[email]
# Note: Update 'root' and '' with your MySQL username and password if different
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:@localhost/gestion_employes"

# Create the SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a scoped session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for the SQLAlchemy models
Base = declarative_base()

# Dependency used in FastAPI endpoints to get the session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
