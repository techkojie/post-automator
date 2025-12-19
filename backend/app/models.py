from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.database import Base

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    content = Column(Text)
    platform = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
