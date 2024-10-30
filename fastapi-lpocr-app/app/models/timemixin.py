from sqlalchemy import Column, DateTime, func
from datetime import datetime

class TimestampMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    modified_at = Column(DateTime(timezone=True), onupdate=datetime.now())
