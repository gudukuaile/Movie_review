from fastapi import APIRouter, Depends, Request, Query
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from models import get_db, Movie, Genre
from fastapi.responses import HTMLResponse
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
    if search:
        query = query.filter(Movie.title.ilike(f"%{search}%"))
    
    # 分类筛选
    if category:
        query = query.join(Movie.genres).join(Genre).filter(Genre.name == category)
    
    # 获取所有分类
    genres = db.query(Genre).all()
    logger.info(f"Found {len(genres)} genres")
    
    # 分页
    per_page = 12
    total = query.count()
    logger.info(f"Total movies: {total}")
    
    movies = query.offset((page - 1) * per_page).limit(per_page).all()
    logger.info(f"Retrieved {len(movies)} movies for page {page}")
    
    # 构建分页对象
    class Pagination:
        def __init__(self, page, per_page, total):
            self.page = page
            self.per_page = per_page
            self.total = total
            self.pages = (total + per_page - 1) // per_page
            self.has_prev = page > 1
            self.has_next = page < self.pages
            self.prev_num = page - 1
            self.next_num = page + 1
        
        def iter_pages(self, left_edge=1, right_edge=1, left_current=2, right_current=2):
            last = 0
            for num in range(1, self.pages + 1):
                if (num <= left_edge or
                    (num > self.page - left_current - 1 and
                     num < self.page + right_current) or
                    num > self.pages - right_edge):
                    if last + 1 != num:
                        yield None
                    yield num
                    last = num
    
    pagination = Pagination(page, per_page, total)
    
    # 打印一些电影信息用于调试
    for movie in movies[:2]:  # 只打印前两部电影的信息
        logger.info(f"Movie: {movie.title}, Rating: {movie.rating}, Genres: {[g.genre.name for g in movie.genres]}")
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "movies": movies,
            "genres": genres,
            "pagination": pagination,
            "search": search,
            "current_category": category
        }
    ) 