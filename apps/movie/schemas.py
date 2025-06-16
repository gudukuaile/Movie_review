from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class MovieBase(BaseModel):
    title: str
    director: str
    actors: str
    year: str
    country: Optional[str] = ""
    duration: Optional[str] = ""
    quote: str
    img_src: Optional[str] = "default.jpg"

class MovieCreate(MovieBase):
    genres: List[str] = []

class MovieUpdate(MovieBase):
    genres: List[str] = []
    new_genre: Optional[str] = ""

class MovieInDB(MovieBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ReviewBase(BaseModel):
    content: str
    rating: int
    movie_id: int

class ReviewCreate(ReviewBase):
    pass

class ReviewInDB(ReviewBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True

