from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Optional
from models import User,Course
from database import init_db, get_session
from contextlib import asynccontextmanager
from models import User, Course, UserCreate
from routers.users import router as users_router
from routers.courses import router as courses_router
from routers.modules import router as modules_router
from routers.enrollment import router as enrollment_router
from routers.quiz import router as quiz_router
from auth import router as auth_router

# Initialize DB on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(courses_router)
app.include_router(modules_router)
app.include_router(enrollment_router)
app.include_router(quiz_router)