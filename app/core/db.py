from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from app.core.config import settings

# Neon-friendly engine:
# - pool_pre_ping  : test conn before use (catches Neon idle drops)
# - pool_recycle   : recycle every 5 min (Neon kills idle ~5 min)
# - pool_size/max_overflow: small, since pooled conn already multiplexes
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=5,
    max_overflow=10,
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

