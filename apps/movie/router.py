from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from models.base import get_db
from models.movie_models import Movie
from models.review_models import Review

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/movie/{movie_id}")
async def movie_detail(
    request: Request,
    movie_id: int,
    db: Session = Depends(get_db)
):
    """电影详情页面"""
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="电影不存在")
    
    # 获取电影的所有评论
    reviews = db.query(Review).filter(Review.movie_id == movie_id).all()
    
    return templates.TemplateResponse(
        "movie_detail.html",
        {
            "request": request,
            "movie": movie,
            "reviews": reviews
        }
    ) 