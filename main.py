from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware # For CORS
from sqlalchemy.orm import Session
from sqlalchemy import func
from apps.common import dependencies as common_deps

import uvicorn

from core.config import settings
from extend.database import engine, Base, SessionLocal, get_db # Import Base and SessionLocal
from models import role_models, user_models, category_models, word_models # Ensure all models are imported for Base.metadata

# Import routers from apps
from apps.user import routes as user_routes
from apps.category import routes as category_routes
from apps.word import routes as word_routes
from apps.main_pages import routes as main_pages_routes
# Import admin-specific logic if needed for dashboard, or it's part of user_routes etc.
from apps.user import crud as user_crud
from apps.user import schemas as user_schemas
from apps.word import crud as word_crud # For word and review counts
# from apps.category import crud as category_crud # If category count is needed

# Create all database tables (if they don't exist)
# This is a simple way for development. For production, Alembic migrations are preferred.
# Base.metadata.create_all(bind=engine) # Moved to startup event

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# --- Static files and Templates (if serving directly from FastAPI) ---
# These might not be needed if you have a separate frontend (e.g., Vue, React)
# that handles all static assets and HTML rendering.
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- CORS Middleware ---
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# --- API Routers ---
app.include_router(main_pages_routes.router) # Routes for serving HTML pages
app.include_router(user_routes.router, prefix=settings.API_V1_STR)
app.include_router(category_routes.router, prefix=settings.API_V1_STR)
app.include_router(word_routes.router, prefix=settings.API_V1_STR)
# Note: The prefix in APIRouter (e.g., "/users") and here will be combined.
# e.g., settings.API_V1_STR + "/users" -> "/api/v1/users"

# --- Application Startup Event ---
@app.on_event("startup")
def on_startup():
    # Create database tables
    # In a production environment, you would typically use Alembic migrations.
    # However, for development or initial setup, this can be useful.
    Base.metadata.create_all(bind=engine)

    # Initialize roles and default admin user
    # This needs a database session.
    db = SessionLocal()
    try:
        role_models.Role.insert_roles(db_session=db) # Call the static method

        # Check if admin user exists, if not create one
        admin_user = user_crud.get_user_by_email(db, email=settings.FIRST_SUPERUSER_EMAIL)
        if not admin_user:
            # This part needs user_schemas to be imported in main.py
            # The python_main_updater script should handle adding this import.
            # For now, assuming user_schemas will be available in the global scope
            # where this function is defined. If not, this will cause a NameError.
            # The script adds 'from apps.user import schemas as user_schemas'.
            user_in = user_schemas.UserCreate(
                username="admin", # Or from settings
                email=settings.FIRST_SUPERUSER_EMAIL,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                # avatar, phone, bio can be None or set from settings
            )
            # Ensure the created user gets the 'Admin' role
            # crud.create_user currently assigns default role. We might need a specific
            # crud.create_superuser or modify create_user to handle this based on email.

            # Simpler approach for now: create user, then assign admin role if not default
            # This assumes create_user doesn't assign admin role by default
            new_admin = user_crud.create_user(db, user_in)
            admin_role = db.query(role_models.Role).filter(role_models.Role.name == 'Admin').first()
            if new_admin and admin_role and new_admin.role.name != 'Admin':
                new_admin.role = admin_role
                db.commit()
                db.refresh(new_admin)
            print(f"Default admin user '{new_admin.username}' created/ensured with email '{new_admin.email}'.")

    finally:
        db.close()

# --- Root Endpoint ---
@app.get("/", tags=["Root"])
async def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}! API docs at /docs or /redoc."}

# --- Admin Dashboard Endpoint ---
# This will provide data for the admin dashboard (similar to Flask admin's dashboard)
# Needs schemas for the response
from pydantic import BaseModel
class DashboardStats(BaseModel):
    user_count: int
    word_count: int # Was movie_count
    review_count: int # Was comment_count
    category_count: int

# This part needs common_deps and func to be imported.
# The python_main_updater script should handle these.
@app.get(f"{settings.API_V1_STR}/admin/dashboard", response_model=DashboardStats,
         dependencies=[Depends(common_deps.requires_admin)], tags=["Admin Dashboard"])
async def get_dashboard_stats(db: Session = Depends(get_db)):
    user_count = user_crud.get_users_count(db)
    word_count = word_crud.get_words_count(db) # Assuming get_words_count exists in word_crud
    review_count = word_crud.get_reviews_count_admin(db) # Assuming exists in word_crud

    # Need category_crud.get_categories_count(db)
    # For now, let's query directly or assume 0
    category_count = db.query(func.count(category_models.Category.id)).scalar() # func from sqlalchemy

    return {
        "user_count": user_count,
        "word_count": word_count,
        "review_count": review_count,
        "category_count": category_count,
    }


if __name__ == "__main__":
    # Note: Uvicorn is usually run from the command line: uvicorn main:app --reload
    uvicorn.run(app, host="0.0.0.0", port=8000)
