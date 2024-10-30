from sqlalchemy import Integer, Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.config.database import Base
from .timemixin import TimestampMixin


class UploadFile(Base, TimestampMixin):
    __tablename__ = "upload_file"

    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    upload_name = Column(String, nullable=False)
    upload_url = Column(String, nullable=False)
    upload_type = Column(String, nullable=False)  # เช่น "image" หรือ "video"

    user = relationship("Users", back_populates="uploads")
