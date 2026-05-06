from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.app.db.init_db import init_db
from backend.app.api.v1.routes.user import router



@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup logic
    init_db()
    yield
    # shutdown logic (in future)


app = FastAPI(lifespan=lifespan)
app.include_router(router=router, prefix="/user")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
