from .base import Base
from .session import engine

# import models so SQLAlchemy registers them
# from app.models import models
from app.models import models  # important

def init_db():
    Base.metadata.create_all(bind=engine)