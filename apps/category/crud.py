from typing import Optional, List
from sqlalchemy.orm import Session

from models.category_models import Category # SQLAlchemy model
from . import schemas # Pydantic schemas

def get_category(db: Session, category_id: int) -> Optional[Category]:
    return db.query(Category).filter(Category.id == category_id).first()

def get_category_by_name(db: Session, name: str) -> Optional[Category]:
    return db.query(Category).filter(Category.name == name).first()

def get_categories(db: Session, skip: int = 0, limit: int = 100) -> List[Category]:
    return db.query(Category).order_by(Category.name).offset(skip).limit(limit).all()

def create_category(db: Session, category: schemas.CategoryCreate) -> Category:
    db_category = Category(name=category.name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def update_category(db: Session, category_id: int, category_update: schemas.CategoryUpdate) -> Optional[Category]:
    db_category = get_category(db, category_id)
    if not db_category:
        return None

    update_data = category_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_category, field, value)

    db.commit()
    db.refresh(db_category)
    return db_category

def delete_category(db: Session, category_id: int) -> Optional[Category]:
    db_category = get_category(db, category_id)
    if db_category:
        # Consider handling words associated with this category:
        # - Option 1: Disallow deletion if words are associated (check db_category.words relationship)
        # - Option 2: Set word's category_id to NULL (if allowed by DB schema)
        # - Option 3: Delete associated words (cascade delete - careful with data loss)
        # - Option 4: Remove associations from WordCategory table only
        # For now, simple deletion of the category itself.
        # If WordCategory has a foreign key constraint, this might fail if words are linked.
        # SQLAlchemy's cascade options on the relationship in the model can also manage this.

        # Example check (requires WordCategory relationship to be eagerly loaded or queried):
        # if db_category.words: # Assuming 'words' is the relationship from Category to WordCategory
        #     raise ValueError("Category cannot be deleted as it is associated with existing words.")

        db.delete(db_category)
        db.commit()
    return db_category
