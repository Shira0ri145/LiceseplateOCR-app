from sqlalchemy import Integer, Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.config.database import Base
from .timemixin import TimestampMixin

class CroppedImage(Base, TimestampMixin):
    __tablename__ = "cropped_image"

    id = Column(Integer, primary_key=True, nullable=False)
    upload_id = Column(Integer, ForeignKey("upload_file.id"), nullable=False)
    crop_image_url = Column(String, nullable=False)  # URL crop
    crop_class_name = Column(String, nullable=False)  # Type Vehicle (เช่น car, truck, bus)
    license_plate = Column(String, nullable=False) 
    crop_timestamp = Column(Integer, nullable=True)  # Time in frame

    upload_file = relationship("UploadFile", back_populates="cropped_images")  # Use string reference


