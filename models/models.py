from datetime import datetime
from sqlalchemy import MetaData, Table, Column, Integer, String, TIMESTAMP, ForeignKey, JSON, create_engine

metadata = MetaData()

user = Table(
    "User",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String, nullable=False),
    Column("username", String, nullable=False),
    Column("hased_password", String, nullable=False),
    Column("permissions", JSON),
    Column("registered_at", TIMESTAMP, default=datetime.utcnow),
)

comment = Table(
    "Comment",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("text", String, nullable=False),
    Column("category", String, nullable=False),
    Column("timestamp", TIMESTAMP, default=datetime.utcnow),
    Column("user_id", Integer, ForeignKey("User.id")),  
)
