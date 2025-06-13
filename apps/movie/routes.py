from fastapi import APIRouter, Depends, HTTPException, Request, Form, File, UploadFile
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from models.base import get_db
from models.role_models import Permission
from fastapi.responses import RedirectResponse
from apps.auth.router import get_current_user
from . import crud, schemas

router = APIRouter()
templates = Jinja2Templates(directory="templates", extensions=["jinja2.ext.do"])

@router.get("/movie/add", name="add_movie")
async def add_movie_page(request: Request, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user or not current_user.can(Permission.MOVIE_EDIT):
        return RedirectResponse(url="/auth/login", status_code=303)
    genres = crud.get_all_genres(db)
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
    
    movie_data = schemas.MovieCreate(
        title=title,
        director=director,
        actors=actors,
        year=year,
        country=country,
        duration=duration,
        quote=description,
        genres=genres
    )
    
    movie = crud.create_movie(db, movie_data, poster_path)
    return RedirectResponse(url=f"/movie/{movie.id}", status_code=303)

@router.get("/movie/{movie_id}", name="movie_detail")
async def movie_detail(
    request: Request,
    movie_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    movie = crud.get_movie(db, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="电影不存在")
    
    reviews = crud.get_movie_reviews(db, movie_id)
    
    return templates.TemplateResponse(
        "movie_detail.html",
        {
            "request": request,
            "movie": movie,
            "reviews": reviews,
            "current_user": current_user,
            "Permission": Permission
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
                "movie": crud.get_movie(db, movie_id),
                "reviews": crud.get_movie_reviews(db, movie_id),
                "current_user": current_user,
                "Permission": Permission,
                "error": "请先登录后再评论！"
            }
        )
    
    movie = crud.get_movie(db, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="电影不存在")
    
    review_data = schemas.ReviewCreate(
        content=content,
        rating=rating,
        movie_id=movie_id
    )
    
    crud.create_review(db, review_data, current_user.id)
    return RedirectResponse(url=f"/movie/{movie_id}?review_success=1", status_code=303)

@router.get("/movie/{movie_id}/edit", name="edit_movie")
async def edit_movie_page(
    request: Request,
    movie_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if not current_user or not current_user.can(Permission.MOVIE_EDIT):
        return RedirectResponse(url="/auth/login", status_code=303)
    
    movie = crud.get_movie(db, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="电影不存在")
    
    genres = crud.get_all_genres(db)
    selected_genres = crud.get_movie_genres(db, movie_id)
    
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
    if not current_user or not current_user.can(Permission.MOVIE_EDIT):
        return RedirectResponse(url="/auth/login", status_code=303)
    
    movie_data = schemas.MovieUpdate(
        title=title,
        director=director,
        actors=actors,
        year=year,
        country=country,
        duration=duration,
        quote=quote,
        genres=genres,
        new_genre=new_genre
    )
    
    movie = crud.update_movie(db, movie_id, movie_data)
    return RedirectResponse(url=f"/movie/{movie.id}", status_code=303)
