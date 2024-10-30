from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from typing import Annotated
from fastapi import Depends
from app.config.settings import get_settings

# setting SQLALCHEMY_DATABASE_URL from Settings
settings = get_settings()

# SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:Qtxh89f5j@localhost:5432/authen"

engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URL) #, echo=True

SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

Base = declarative_base()

# Dependency
async def get_db():

    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()

db_dependency = Annotated[Session, Depends(get_db)]
