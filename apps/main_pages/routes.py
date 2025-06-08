from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional # Added for Optional search and category

from extend.database import get_db
# Assuming word_crud and schemas are needed for index page
from apps.word import crud as word_crud
from apps.word import schemas as word_schemas
from apps.category import crud as category_crud # For category list on index
from apps.category import schemas as category_schemas

# Assuming user_auth for optional current user on index page
from apps.user import auth as user_auth
from models.user_models import User as UserModel


router = APIRouter(
    tags=["Frontend Pages"],
    include_in_schema=False # Typically, HTML serving routes are not part of the API schema
)

templates = Jinja2Templates(directory="templates")

@router.get("/", name="home_page")
async def get_home_page(
    request: Request,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10, # Default items per page
    search: Optional[str] = None,
    category: Optional[str] = None,
    current_user: Optional[UserModel] = Depends(user_auth.get_optional_current_user)
):
    words = word_crud.get_words(db, skip=skip, limit=limit, search=search, category_name=category)
    total_words = word_crud.get_words_count(db, search=search, category_name=category)
    all_categories = category_crud.get_categories(db, limit=100) # Get all categories for filter dropdown

    # Basic pagination logic (can be improved)
    # Ensure total_pages is at least 1, even if total_words is 0
    total_pages = (total_words + limit - 1) // limit if total_words > 0 else 1
    current_page = skip // limit + 1

    pagination = {
        "page": current_page,
        "per_page": limit,
        "total_items": total_words,
        "total_pages": total_pages,
        "items_on_page": len(words),
        "has_prev": current_page > 1,
        "has_next": current_page < total_pages,
        "prev_num": current_page -1, # For template page numbers
        "next_num": current_page +1, # For template page numbers
    }

    return templates.TemplateResponse("index.html", {
        "request": request,
        "words": words, # Renamed from 'movies' for consistency with new model
        "categories": all_categories, # Renamed from 'genres'
        "current_category": category,
        "search": search,
        "pagination": pagination,
        "current_user": current_user, # Pass current_user to template
        # "Permission": models.role_models.Permission # If needed in template
    })



@router.get("/words/{word_id}/view", name="word_detail_page", include_in_schema=False)
async def get_word_detail_page(
    request: Request,
    word_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[UserModel] = Depends(user_auth.get_optional_current_user)
):
    db_word = word_crud.get_word(db, word_id=word_id) # This crud loads categories and reviews
    if db_word is None:
        return templates.TemplateResponse("404.html", {"request": request, "detail": "Word not found"}, status_code=404)

    return templates.TemplateResponse("word_detail.html", {
        "request": request,
        "word": db_word,
        "current_user": current_user,
    })
