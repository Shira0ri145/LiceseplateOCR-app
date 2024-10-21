from sqlalchemy import Boolean, Integer, Column, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from datetime import datetime
"""from sqlalchemy.orm.session import Session"""
from app.config.database import Base

class TimestampMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    modified_at = Column(DateTime(timezone=True), onupdate=datetime.now())

class Users(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String(25), unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    image_url = Column(String, nullable=False, default="https://example.com/default-profile.png")
    user_id = Column(Integer, nullable=True)
    is_verified = Column(Boolean, default=False)
    verified_at = Column(DateTime(timezone=True), onupdate=datetime.now())

    roles = relationship("Roles", secondary="users_roles", back_populates="users")

class UsersRoles(Base, TimestampMixin):
    __tablename__ = "users_roles"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id"), primary_key=True)

class Roles(Base):

    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, nullable=False)
    role_name = Column(String,nullable=False)

    users = relationship("Users", secondary="users_roles", back_populates="roles")
