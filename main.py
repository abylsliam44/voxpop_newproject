from fastapi import FastAPI, Response, Query, HTTPException, Depends, Form
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from models.models import metadata, user, comment
from pydantic import BaseModel
from passlib.context import CryptContext
from sqlmodel import Session, select, SQLModel, select
from sqlalchemy.orm import Session as SQLAlchemySession
from datetime import datetime
from typing import Optional
from config import DB_HOST, DB_PORT, DB_USER, DB_NAME, DB_PASS
from fastapi.responses import HTMLResponse
from typing import Optional
from fastapi_users import schemas

from datetime import datetime
from enum import Enum
from typing import List, Optional, Union

from fastapi_users import fastapi_users, FastAPIUsers
from pydantic import BaseModel, Field

from fastapi import FastAPI, Request, status, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from auth.auth import auth_backend
from auth.database import User
from auth.manager import get_user_manager
from auth.schemas import UserRead, UserCreate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
app = FastAPI()

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


user_table = Table('User', metadata, autoload_with=engine)
comment_table = Table('Comment', metadata, autoload_with=engine)

class UserCreate(BaseModel):
    email: str
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    registered_at: datetime


@app.post("/register/user/", response_model=UserResponse)
def register_user(
    email: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    db: SessionLocal = Depends(get_db)
):
    hashed_password = pwd_context.hash(password)

    try:
        result = db.execute(
            user_table.insert().values(
                email=email,
                username=username,
                hashed_password=hashed_password,
                registered_at=datetime.utcnow()
            )
        )
        db.commit()
        new_user_id = result.inserted_primary_key[0]
        new_user = db.execute(
            user_table.select().where(user_table.c.id == new_user_id)
        ).fetchone()

        if new_user is None:
            raise HTTPException(status_code=404, detail="User not found")

        return UserResponse(
            id=new_user.id,
            email=new_user.email,
            username=new_user.username,
            registered_at=new_user.registered_at
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/register/", response_class=HTMLResponse)
def read_root():
    return """
    <html>
        <head>
            <title>Register</title>
        </head>
        <body>
            <h1>Register User</h1>
            <form action="/register/user/" method="post">
                <label for="email">Email:</label>
                <input type="text" id="email" name="email"><br><br>
                <label for="username">Username:</label>
                <input type="text" id="username" name="username"><br><br>
                <label for="password">Password:</label>
                <input type="password" id="password" name="password"><br><br>
                <input type="submit" value="Register">
            </form>
        </body>
    </html>
    """

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

current_user = fastapi_users.current_user()

@app.get("/protected-route")
def protected_route(user: User = Depends(current_user)):
    return f"Hello, {user.username}"


@app.get("/unprotected-route")
def unprotected_route():
    return f"Hello, anonym"