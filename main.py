from fastapi import FastAPI, Response, Query, HTTPException, Depends
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from models.models import metadata, user, comment
from pydantic import BaseModel
from typing import List
from passlib.context import CryptContext
from sqlmodel import Session, select, SQLModel, select
from sqlalchemy.orm import Session as SQLAlchemySession
from datetime import datetime
from passlib.context import CryptContext
from typing import Optional
from config import DB_HOST, DB_PORT, DB_USER, DB_NAME, DB_PASS

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



@app.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: SessionLocal = Depends(get_db)):
    hashed_password = pwd_context.hash(user.password)

    try:
        # Insert user into the database using the SQLAlchemy Table object
        result = db.execute(
            user_table.insert().values(
                email=user.email,
                username=user.username,
                hased_password=hashed_password,
                registered_at=datetime.utcnow()
            )
        )
        db.commit()

        new_user_id = result.inserted_primary_key[0]

        # Fetch the newly created user
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
