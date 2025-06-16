from fastapi import APIRouter, Depends, Request, Query
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from models import get_db, Movie, Genre, MovieGenre, User
from fastapi.responses import HTMLResponse
from utils.pagination import Pagination
import logging
from apps.auth.router import get_current_user  # 导入获取当前用户的依赖
from models.role_models import Permission

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="templates", extensions=["jinja2.ext.do"])

@router.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    page: int = Query(1, ge=1),
    search: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # 添加当前用户
):
    # 构建查询
    query = db.query(Movie)
    
    # 搜索功能
    if search and search != 'None':
        query = query.filter(Movie.title.ilike(f"%{search}%"))
    
    # 分类筛选
    if category:
        # 修改查询逻辑，使用正确的关联查询
        query = (query
                .join(MovieGenre, Movie.id == MovieGenre.movie_id)
                .join(Genre, MovieGenre.genre_id == Genre.id)
                .filter(Genre.name == category))
    
    # 获取所有分类
    genres = db.query(Genre).all()
    
    # 分页
    per_page = 12
    total = query.count()
    
    movies = query.offset((page - 1) * per_page).limit(per_page).all()
    
    pagination = Pagination(page, per_page, total)
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "movies": movies,
            "genres": genres,
            "pagination": pagination,
            "search": search if search != 'None' else None,
            "current_category": category,
            "current_user": current_user,
            "Permission": Permission  # 传递 Permission
        }
    ) 