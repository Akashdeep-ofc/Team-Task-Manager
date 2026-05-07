from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker
from app.core.config import settings



sql_connect = URL.create(
    "postgresql+psycopg",
    username=settings.username,
    password=settings.password,
    host=settings.host,
    database=settings.database,
    port=settings.port
)


engine = create_engine(sql_connect)


if settings.database_url:
    DATABASE_URL = settings.database_url
    engine = create_engine(url=DATABASE_URL)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    except:
        db.rollback()
        raise
    finally:
        db.close()