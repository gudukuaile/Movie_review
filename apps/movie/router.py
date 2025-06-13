from fastapi import APIRouter, Depends, HTTPException, Request, Form, File, UploadFile
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from models.base import get_db
from models.movie_models import Movie, Genre, MovieGenre
from models.review_models import Review
from apps.auth.router import get_current_user  # 导入获取当前用户的依赖
from models.role_models import Permission
from fastapi.responses import RedirectResponse

router = APIRouter()
templates = Jinja2Templates(directory="templates", extensions=["jinja2.ext.do"])

@router.get("/movie/add", name="add_movie")
async def add_movie_page(request: Request, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user or not current_user.can(Permission.MOVIE_EDIT):
        return RedirectResponse(url="/auth/login", status_code=303)
    genres = db.query(Genre).all()
    return templates.TemplateResponse(
        "add_movie.html",
        {"request": request, "current_user": current_user, "genres": genres, "Permission": Permission}
    )

@router.post("/movie/add", name="add_movie_post")
async def add_movie(
    request: Request,
    title: str = Form(...),
    director: str = Form(...),
    actors: str = Form(...),
    year: str = Form(...),
    country: str = Form(""),
    duration: str = Form(""),
    description: str = Form(...),
    genres: list = Form([]),
    poster: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if not current_user or not current_user.can(Permission.MOVIE_EDIT):
        return RedirectResponse(url="/auth/login", status_code=303)
    poster_path = "default.jpg"
    if poster and poster.filename:
        file_location = f"uploads/{poster.filename}"
        with open(file_location, "wb") as f:
            f.write(await poster.read())
        poster_path = file_location
    movie = Movie(
        title=title,
        director=director,
        actors=actors,
        year=year,
        country=country,
        duration=duration,
        quote=description,
        img_src=poster_path
    )
    db.add(movie)
    db.commit()
    for genre_name in genres:
        genre = db.query(Genre).filter_by(name=genre_name).first()
        if not genre:
            genre = Genre(name=genre_name)
            db.add(genre)
            db.commit()
        movie_genre = MovieGenre(movie_id=movie.id, genre_id=genre.id)
        db.add(movie_genre)
    db.commit()
    return RedirectResponse(url=f"/movie/{movie.id}", status_code=303)

@router.get("/movie/{movie_id}", name="movie_detail")
async def movie_detail(
    request: Request,
    movie_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # 添加 current_user
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
            "reviews": reviews,
            "current_user": current_user,
            "Permission": Permission  # 传递 Permission
        }
    )

@router.post("/movie/{movie_id}/review", name="add_review")
async def add_review(
    request: Request,
    movie_id: int,
    content: str = Form(...),
    rating: int = Form(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if not current_user:
        return templates.TemplateResponse(
            "movie_detail.html",
            {
                "request": request,
                "movie": db.query(Movie).filter(Movie.id == movie_id).first(),
                "reviews": db.query(Review).filter(Review.movie_id == movie_id).all(),
                "current_user": current_user,
                "Permission": Permission,
                "error": "请先登录后再评论！"
            }
        )
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="电影不存在")
    review = Review(
        content=content,
        rating=rating,
        user_id=current_user.id,
        movie_id=movie_id
    )
    db.add(review)
    db.commit()
    return RedirectResponse(url=f"/movie/{movie_id}?review_success=1", status_code=303)

@router.get("/movie/{movie_id}/edit", name="edit_movie")
async def edit_movie_page(
    request: Request,
    movie_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """编辑电影页面"""
    if not current_user or not current_user.can(Permission.MOVIE_EDIT):
        return RedirectResponse(url="/auth/login", status_code=303)
    
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="电影不存在")
    
    genres = db.query(Genre).all()
    selected_genres = [g.genre.name for g in movie.genres]
    
    return templates.TemplateResponse(
        "movie/edit_movie.html",
        {
            "request": request,
            "movie": movie,
            "all_genres": genres,
            "selected_genres": selected_genres,
            "current_user": current_user,
            "Permission": Permission
        }
    )

@router.post("/movie/{movie_id}/edit", name="edit_movie_post")
async def edit_movie(
    request: Request,
    movie_id: int,
    title: str = Form(...),
    director: str = Form(...),
    actors: str = Form(...),
    year: str = Form(...),
    country: str = Form(""),
    duration: str = Form(""),
    quote: str = Form(...),
    genres: list = Form([]),
    new_genre: str = Form(""),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """处理编辑电影的请求"""
    if not current_user or not current_user.can(Permission.MOVIE_EDIT):
        return RedirectResponse(url="/auth/login", status_code=303)
    
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="电影不存在")
    
    # 更新电影基本信息
    movie.title = title
    movie.director = director
    movie.actors = actors
    movie.year = year
    movie.country = country
    movie.duration = duration
    movie.quote = quote
    
    # 处理新类型
    if new_genre:
        genres.append(new_genre)
    
    # 更新电影类型
    # 首先删除所有现有的类型关联
    db.query(MovieGenre).filter(MovieGenre.movie_id == movie.id).delete()
    
    # 然后添加新的类型关联
    for genre_name in genres:
        genre = db.query(Genre).filter_by(name=genre_name).first()
        if not genre:
            genre = Genre(name=genre_name)
            db.add(genre)
            db.commit()
        movie_genre = MovieGenre(movie_id=movie.id, genre_id=genre.id)
        db.add(movie_genre)
    
    db.commit()
    return RedirectResponse(url=f"/movie/{movie.id}", status_code=303) 