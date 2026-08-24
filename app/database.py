from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from . import config

engine = create_engine(config.settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Yield a DB session and close it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
