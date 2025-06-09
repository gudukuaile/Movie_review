from fastapi import APIRouter, Depends, Request, Query
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from models import get_db, Movie, Genre, MovieGenre
from fastapi.responses import HTMLResponse
from utils.pagination import Pagination
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    page: int = Query(1, ge=1),
    search: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    # 构建查询
    query = db.query(Movie)
    
    # 搜索功能
    if search and search != 'None':
        query = query.filter(Movie.title.ilike(f"%{search}%"))
    
    # 分类筛选
    if category:
        logger.info(f"Filtering by category: {category}")
        # 修改查询逻辑，使用正确的关联查询
        query = (query
                .join(MovieGenre, Movie.id == MovieGenre.movie_id)
                .join(Genre, MovieGenre.genre_id == Genre.id)
                .filter(Genre.name == category))
        logger.info(f"SQL Query: {query}")
    
    # 获取所有分类
    genres = db.query(Genre).all()
    logger.info(f"Found {len(genres)} genres")
    for genre in genres:
        logger.info(f"Genre: {genre.name}")
    
    # 分页
    per_page = 12
    total = query.count()
    logger.info(f"Total movies: {total}")
    
    movies = query.offset((page - 1) * per_page).limit(per_page).all()
    logger.info(f"Retrieved {len(movies)} movies for page {page}")
    
    # 打印查询到的电影信息
    for movie in movies:
        logger.info(f"Movie: {movie.title}")
        logger.info(f"Genres: {[g.genre.name for g in movie.genres]}")
    
    pagination = Pagination(page, per_page, total)
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "movies": movies,
            "genres": genres,
            "pagination": pagination,
            "search": search if search != 'None' else None,
            "current_category": category
        }
    ) 