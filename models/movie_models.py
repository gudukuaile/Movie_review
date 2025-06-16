from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from .base import Base

class Genre(Base):
    __tablename__ = 'genres'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    movies = relationship('MovieGenre', back_populates='genre')

class MovieGenre(Base):
    __tablename__ = 'movie_genres'

    id = Column(Integer, primary_key=True)
    movie_id = Column(Integer, ForeignKey('movies.id'), nullable=False)
    genre_id = Column(Integer, ForeignKey('genres.id'), nullable=False)
    movie = relationship('Movie', back_populates='genres')
    genre = relationship('Genre', back_populates='movies')

class Movie(Base):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True)
    link = Column(String(255))
    img_src = Column(String(255))
    title = Column(String(100))
    rating = Column(Float)
    judge_num = Column(Integer)
    quote = Column(Text)
    director = Column(String(100))
    actors = Column(String(200))
    year = Column(String(10))
    country = Column(String(50))
    duration = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)

    genres = relationship('MovieGenre', back_populates='movie', lazy='joined')
    reviews = relationship('Review', back_populates='movie', lazy='dynamic')
