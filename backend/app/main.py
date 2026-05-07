from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.db.init_db import init_db
from app.api.v1.routes.user import router
from app.core.config import settings



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



FRONTEND_URL = settings.frontend_url
# print(FRONTEND_URL)



app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router=router, prefix="/user")

