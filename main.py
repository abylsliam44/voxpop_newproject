from fastapi import FastAPI, Response, Query, HTTPException, Depends
from sqlalchemy import create_engine, MetaData
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

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
app = FastAPI()



def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


class UserCreate(BaseModel):
    email: str
    username: str
    password: str

# Модель Pydantic для ответа
class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    registered_at: datetime



@app.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Hash the password
    hashed_password = pwd_context.hash(user.password)

    # Create a new User instance with hashed password
    db_user = user(email=user.email, username=user.username, hashed_password=hashed_password, registered_at=datetime.utcnow())

    # Add the user to the session and commit to database
    db.add(db_user)
    db.commit()

    # Refresh the user object to fetch updated data (like auto-generated ID)
    db.refresh(db_user)

    # Return the user response
    return UserResponse(id=db_user.id, email=db_user.email, username=db_user.username, registered_at=db_user.registered_at)

