from fastapi import FastAPI
from contextlib import asynccontextmanager
from backend.app.db.init_db import init_db
from backend.app.api.v1.routes import auth




@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup logic
    init_db()
    yield
    # shutdown logic (optional)


app = FastAPI(lifespan=lifespan)


# app.include_router(auth.router, prefix="/api/v1")