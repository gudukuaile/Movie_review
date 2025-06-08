import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base

# Association table for Word and Category (many-to-many)
class WordCategory(Base):
    __tablename__ = 'word_categories' # Renamed from 'movie_genres'
    id = Column(Integer, primary_key=True, index=True)
    word_id = Column(Integer, ForeignKey('words.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)

    word = relationship('Word', back_populates='categories_association') # Changed relationship name
    category = relationship('Category', back_populates='words')

class Word(Base):
    __tablename__ = 'words' # Renamed from 'movies'
    id = Column(Integer, primary_key=True, index=True)
    # link = Column(String(255), nullable=True) # Specific to movies, might remove or repurpose
    img_src = Column(String(255), nullable=True) # Image for the word/concept
    title = Column(String(100), nullable=False, index=True) # The word/term itself
    rating = Column(Float, nullable=True) # Could be user rating or importance
    # judge_num = Column(Integer, nullable=True) # Number of ratings/reviews
    quote = Column(Text, nullable=True) # Definition, example sentence, or description
    # director = Column(String(100), nullable=True) # Not applicable for 'word'
    # actors = Column(String(200), nullable=True) # Not applicable for 'word'
    # year = Column(String(10), nullable=True) # Not applicable for 'word'
    # country = Column(String(50), nullable=True) # Not applicable for 'word'
    # duration = Column(String(20), nullable=True) # Not applicable for 'word'
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationship to the association table WordCategory
    categories_association = relationship('WordCategory', back_populates='word') # Changed relationship name

    # Relationship to Review model
    reviews = relationship('Review', back_populates='word') # word instead of movie

class Review(Base):
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    rating = Column(Integer, nullable=True) # User's rating for the word/concept
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    author = relationship('User') # Simpler relationship to User

    word_id = Column(Integer, ForeignKey('words.id'), nullable=False) # Changed from movie_id
    word = relationship('Word', back_populates='reviews')
