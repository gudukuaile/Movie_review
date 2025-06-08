from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from models.base import Base

class Category(Base):
    __tablename__ = 'categories' # Renamed from 'genres'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)

    # Relationship to the association table WordCategory
    words = relationship('WordCategory', back_populates='category')
