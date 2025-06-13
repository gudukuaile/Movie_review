from sqlalchemy.orm import Session
from models.movie_models import Movie, Genre, MovieGenre
from models.review_models import Review
from . import schemas
from fastapi import HTTPException

def get_movie(db: Session, movie_id: int):
    return db.query(Movie).filter(Movie.id == movie_id).first()

def get_movie_reviews(db: Session, movie_id: int):
    return db.query(Review).filter(Review.movie_id == movie_id).all()

def create_movie(db: Session, movie: schemas.MovieCreate, poster_path: str = "default.jpg"):
    db_movie = Movie(
        title=movie.title,
        director=movie.director,
        actors=movie.actors,
        year=movie.year,
        country=movie.country,
        duration=movie.duration,
        quote=movie.quote,
        img_src=poster_path
    )
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    
    # 处理电影类型
    for genre_name in movie.genres:
        genre = db.query(Genre).filter_by(name=genre_name).first()
        if not genre:
            genre = Genre(name=genre_name)
            db.add(genre)
            db.commit()
        movie_genre = MovieGenre(movie_id=db_movie.id, genre_id=genre.id)
        db.add(movie_genre)
    db.commit()
    return db_movie

def update_movie(db: Session, movie_id: int, movie: schemas.MovieUpdate):
    db_movie = get_movie(db, movie_id)
    if not db_movie:
        raise HTTPException(status_code=404, detail="电影不存在")
    
    # 更新电影基本信息
    for key, value in movie.dict(exclude={'genres', 'new_genre'}).items():
        setattr(db_movie, key, value)
    
    # 处理新类型
    genres = movie.genres
    if movie.new_genre:
        genres.append(movie.new_genre)
    
    # 更新电影类型
    db.query(MovieGenre).filter(MovieGenre.movie_id == movie_id).delete()
    
    for genre_name in genres:
        genre = db.query(Genre).filter_by(name=genre_name).first()
        if not genre:
            genre = Genre(name=genre_name)
            db.add(genre)
            db.commit()
        movie_genre = MovieGenre(movie_id=movie_id, genre_id=genre.id)
        db.add(movie_genre)
    
    db.commit()
    db.refresh(db_movie)
    return db_movie

def create_review(db: Session, review: schemas.ReviewCreate, user_id: int):
    db_review = Review(
        content=review.content,
        rating=review.rating,
        user_id=user_id,
        movie_id=review.movie_id
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

def get_all_genres(db: Session):
    return db.query(Genre).all()

def get_movie_genres(db: Session, movie_id: int):
    movie = get_movie(db, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="电影不存在")
    return [g.genre.name for g in movie.genres]
