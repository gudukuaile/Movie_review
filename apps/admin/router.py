from fastapi import APIRouter, Depends, Request, Form, Query, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from models import get_db, User, Movie, Review, MovieGenre, Genre
from apps.auth.router import get_current_user
from models.role_models import Permission, Role
from utils.pagination import Pagination
import os
import shutil
from pathlib import Path
from datetime import datetime

router = APIRouter()
templates = Jinja2Templates(directory="templates", extensions=["jinja2.ext.do"])

# 头像上传配置
AVATAR_UPLOAD_DIR = "static/uploads/avatars"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB

# 确保上传目录存在
os.makedirs(AVATAR_UPLOAD_DIR, exist_ok=True)

def allowed_file(filename):
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS

@router.get("/admin/dashboard", name="dashboard")
async def dashboard(request: Request, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if not current_user or not current_user.can(Permission.ADMIN):
        return RedirectResponse(url="/auth/login", status_code=303)
    user_count = db.query(User).count()
    movie_count = db.query(Movie).count()
    comment_count = db.query(Review).count()
    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "current_user": current_user,
            "user_count": user_count,
            "movie_count": movie_count,
            "comment_count": comment_count,
            "Permission": Permission
        }
    )

@router.get("/admin/users", name="manage_users")
async def manage_users(request: Request, db: Session = Depends(get_db), current_user=Depends(get_current_user), page: int = Query(1, ge=1)):
    if not current_user or not current_user.can(Permission.ADMIN):
        return RedirectResponse(url="/auth/login", status_code=303)
    
    per_page = 10
    
    query = db.query(User).order_by(User.created_at.desc())
    total = query.count()
    users = query.offset((page - 1) * per_page).limit(per_page).all()
    
    pagination = Pagination(page, per_page, total)

    return templates.TemplateResponse(
        "admin/users.html",
        {
            "request": request,
            "current_user": current_user,
            "users": users,
            "pagination": pagination,
            "Permission": Permission
        }
    )

@router.get("/admin/user/{id}/edit", name="edit_user")
async def edit_user_page(id: int, request: Request, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if not current_user or not current_user.can(Permission.ADMIN):
        return RedirectResponse(url="/auth/login", status_code=303)
    user = db.query(User).filter(User.id == id).first()
    roles = db.query(Role).all()
    return templates.TemplateResponse(
        "admin/edit_user.html",
        {
            "request": request,
            "current_user": current_user,
            "user": user,
            "roles": roles,
            "Permission": Permission
        }
    )

@router.post("/admin/user/{id}/edit")
async def edit_user(
    id: int,
    request: Request,
    role_id: int = Form(None),
    reset_password: str = Form(None),
    avatar: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if not current_user or not current_user.can(Permission.ADMIN):
        return RedirectResponse(url="/auth/login", status_code=303)
    user = db.query(User).filter(User.id == id).first()
    if user:
        try:
            if role_id:
                role = db.query(Role).filter(Role.id == role_id).first()
                if role:
                    user.role = role
            if reset_password:
                from utils.security import generate_password_hash
                user.password_hash = generate_password_hash(reset_password)
            
            # 处理头像上传
            if avatar and avatar.filename:
                if not allowed_file(avatar.filename):
                    request.session["message"] = "不支持的文件格式，请上传jpg、png或gif格式的图片"
                    request.session["message_type"] = "danger"
                    return RedirectResponse(url=f"/admin/user/{id}/edit", status_code=303)
                
                # 生成唯一的文件名
                file_ext = Path(avatar.filename).suffix
                new_filename = f"{user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}{file_ext}"
                file_path = os.path.join(AVATAR_UPLOAD_DIR, new_filename)
                
                try:
                    # 保存文件
                    with open(file_path, "wb") as buffer:
                        shutil.copyfileobj(avatar.file, buffer)
                    
                    # 更新用户头像URL
                    user.avatar = f"/static/uploads/avatars/{new_filename}"
                except Exception as e:
                    request.session["message"] = "头像上传失败，请重试"
                    request.session["message_type"] = "danger"
                    return RedirectResponse(url=f"/admin/user/{id}/edit", status_code=303)
            
            db.commit()
            request.session["message"] = "用户更新成功！"
            request.session["message_type"] = "success"
        except Exception as e:
            db.rollback()
            request.session["message"] = f"用户更新失败：{str(e)}"
            request.session["message_type"] = "danger"
    else:
        request.session["message"] = "用户未找到！"
        request.session["message_type"] = "danger"
    return RedirectResponse(url="/admin/users", status_code=303)

@router.get("/admin/movies", name="manage_movies")
async def manage_movies(request: Request, db: Session = Depends(get_db), current_user=Depends(get_current_user), page: int = Query(1, ge=1)):
    if not current_user or not current_user.can(Permission.ADMIN):
        return RedirectResponse(url="/auth/login", status_code=303)
    
    per_page = 10
    
    query = db.query(Movie).order_by(Movie.created_at.desc() if hasattr(Movie, 'created_at') else Movie.id.desc())
    total = query.count()
    movies = query.offset((page - 1) * per_page).limit(per_page).all()
    
    pagination = Pagination(page, per_page, total)

    return templates.TemplateResponse(
        "admin/movies.html",
        {
            "request": request,
            "current_user": current_user,
            "movies": movies,
            "pagination": pagination,
            "Permission": Permission
        }
    )

@router.get("/admin/movie/{id}/delete", name="delete_movie")
async def delete_movie(id: int, request: Request, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if not current_user or not current_user.can(Permission.MOVIE_DELETE):
        return RedirectResponse(url="/auth/login", status_code=303)
    movie = db.query(Movie).filter(Movie.id == id).first()
    if movie:
        try:
            # 删除与电影相关的评论
            db.query(Review).filter(Review.movie_id == id).delete(synchronize_session=False)
            # 删除电影与类型的关联
            db.query(MovieGenre).filter(MovieGenre.movie_id == id).delete(synchronize_session=False)
            db.delete(movie)
            db.commit()
            request.session["message"] = "电影删除成功！"
            request.session["message_type"] = "success"
        except Exception as e:
            db.rollback()
            request.session["message"] = f"电影删除失败：{str(e)}"
            request.session["message_type"] = "danger"
    else:
        request.session["message"] = "电影未找到！"
        request.session["message_type"] = "danger"
    return RedirectResponse(url="/admin/movies", status_code=303)

@router.get("/admin/reviews", name="manage_reviews")
async def manage_reviews(request: Request, db: Session = Depends(get_db), current_user=Depends(get_current_user), page: int = Query(1, ge=1)):
    if not current_user or not current_user.can(Permission.ADMIN):
        return RedirectResponse(url="/auth/login", status_code=303)
    
    per_page = 10
    
    query = db.query(Review).order_by(Review.created_at.desc())
    total = query.count()
    reviews = query.offset((page - 1) * per_page).limit(per_page).all()
    
    pagination = Pagination(page, per_page, total)

    return templates.TemplateResponse(
        "admin/reviews.html",
        {
            "request": request,
            "current_user": current_user,
            "reviews": reviews,
            "pagination": pagination,
            "Permission": Permission
        }
    )

@router.get("/admin/review/{id}/edit", name="edit_review")
async def edit_review_page(id: int, request: Request, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if not current_user or not current_user.can(Permission.ADMIN):
        return RedirectResponse(url="/auth/login", status_code=303)
    review = db.query(Review).filter(Review.id == id).first()
    return templates.TemplateResponse(
        "admin/edit_review.html",
        {
            "request": request,
            "current_user": current_user,
            "review": review,
            "Permission": Permission
        }
    )

@router.post("/admin/review/{id}/edit")
async def edit_review(
    id: int,
    request: Request,
    content: str = Form(...),
    rating: int = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if not current_user or not current_user.can(Permission.ADMIN):
        return RedirectResponse(url="/auth/login", status_code=303)
    review = db.query(Review).filter(Review.id == id).first()
    if review:
        review.content = content
        review.rating = rating
        try:
            db.commit()
            request.session["message"] = "评论更新成功！"
            request.session["message_type"] = "success"
        except Exception as e:
            db.rollback()
            request.session["message"] = f"评论更新失败：{str(e)}"
            request.session["message_type"] = "danger"
    else:
        request.session["message"] = "评论未找到！"
        request.session["message_type"] = "danger"
    return RedirectResponse(url="/admin/reviews", status_code=303)

@router.get("/admin/review/{id}/delete", name="delete_review")
async def delete_review(id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if not current_user or not current_user.can(Permission.ADMIN):
        return RedirectResponse(url="/auth/login", status_code=303)
    review = db.query(Review).filter(Review.id == id).first()
    db.delete(review)
    db.commit()
    return RedirectResponse(url="/admin/reviews", status_code=303)

@router.get("/admin/movie/{id}/edit", name="admin_edit_movie_page")
async def edit_movie_page(id: int, request: Request, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if not current_user or not current_user.can(Permission.ADMIN):
        return RedirectResponse(url="/auth/login", status_code=303)
    movie = db.query(Movie).filter(Movie.id == id).first()
    if not movie:
        request.session["message"] = "电影未找到！"
        request.session["message_type"] = "danger"
        return RedirectResponse(url="/admin/movies", status_code=303)
    
    all_genres = db.query(Genre).all() # Fetch all genres
    selected_genres = [g.genre.name for g in movie.genres] # Get names of selected genres

    from datetime import datetime
    now = datetime.now()

    return templates.TemplateResponse(
        "admin/edit_movie.html",
        {
            "request": request,
            "current_user": current_user,
            "movie": movie,
            "all_genres": all_genres,
            "selected_genres": selected_genres,
            "now": now,
            "Permission": Permission
        }
    )

@router.post("/admin/movie/{id}/edit", name="admin_edit_movie_post")
async def edit_movie(
    id: int,
    request: Request,
    title: str = Form(...),
    release_year: int = Form(...),
    director: str = Form(...),
    quote: str = Form(...),
    poster: str = Form(None),
    genres: list = Form([]),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if not current_user or not current_user.can(Permission.ADMIN):
        return RedirectResponse(url="/auth/login", status_code=303)
    movie = db.query(Movie).filter(Movie.id == id).first()
    if movie:
        print(f"DEBUG: Attempting to save movie {movie.id} with title {title}") # TEMP DEBUG
        try:
            movie.title = title
            movie.release_year = release_year
            movie.director = director
            movie.quote = quote

            if poster: # Only update if a new poster URL is provided
                movie.poster = poster
            
            # 处理电影类型
            # 首先删除所有现有的类型关联
            db.query(MovieGenre).filter(MovieGenre.movie_id == movie.id).delete()
            db.flush() # Flush to ensure delete happens before adding new ones

            # 添加新的类型关联
            for genre_name in genres:
                genre_obj = db.query(Genre).filter(Genre.name == genre_name).first()
                if not genre_obj:
                    genre_obj = Genre(name=genre_name)
                    db.add(genre_obj)
                    db.flush() # Ensure genre_obj gets an ID if it's new
                movie_genre = MovieGenre(movie_id=movie.id, genre_id=genre_obj.id)
                db.add(movie_genre)

            db.commit()
            request.session["message"] = "电影更新成功！"
            request.session["message_type"] = "success"
            print("DEBUG: Movie saved successfully, redirecting.") # TEMP DEBUG
        except Exception as e:
            db.rollback()
            request.session["message"] = f"电影更新失败：{str(e)}"
            request.session["message_type"] = "danger"
            print(f"DEBUG: Movie save failed: {str(e)}") # TEMP DEBUG
    else:
        request.session["message"] = "电影未找到！"
        request.session["message_type"] = "danger"
        print("DEBUG: Movie not found for editing.") # TEMP DEBUG
    return RedirectResponse(url="/admin/movies", status_code=303) 