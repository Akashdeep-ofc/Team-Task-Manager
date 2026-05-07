from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.db.init_db import init_db
from app.api.v1.routes.user import router



@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup logic
    try:
        init_db()
        print("✅ DB connected")
    except Exception as e:
        print("❌ DB connection failed:", e)
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
