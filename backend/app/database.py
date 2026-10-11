import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

logger = logging.getLogger("uvicorn.error")

Base = declarative_base()

ACTIVE_DB_TYPE = "MySQL"
engine = None
SessionLocal = None


def init_engine():
    global engine, SessionLocal, ACTIVE_DB_TYPE
    db_url = settings.DATABASE_URL

    try:
        # First attempt with configured DATABASE_URL (MySQL)
        test_engine = create_engine(
            db_url,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False
        )
        with test_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("[Database] Successfully connected to MySQL database.")
        engine = test_engine
        ACTIVE_DB_TYPE = "MySQL"
    except Exception as e:
        if settings.DB_AUTO_FALLBACK_SQLITE:
            logger.warning(
                f"[Database] Could not connect to MySQL ({e}). "
                "Falling back to local SQLite database (sqlite:///./tasks.db) for full local availability."
            )
            fallback_url = "sqlite:///./tasks.db"
            engine = create_engine(
                fallback_url,
                connect_args={"check_same_thread": False},
                echo=False
            )
            ACTIVE_DB_TYPE = "SQLite (Fallback)"
        else:
            raise e

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine


# Initialize engine on import
init_engine()


def get_db():
    """Dependency that provides an active database session for requests."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
