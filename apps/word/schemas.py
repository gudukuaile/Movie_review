from pydantic import BaseModel, constr, conint, confloat
from typing import Optional, List
import datetime

# Import schemas from other apps for nested responses
# Need to use forward references if there are circular dependencies,
# or ensure they are defined in a way that Pydantic can resolve them.
# For now, we'll use string literals for forward references and call update_forward_refs() later.
from apps.user.schemas import UserRead
from apps.category.schemas import CategoryRead

# --- Review Schemas ---
class ReviewBase(BaseModel):
    content: constr(min_length=1)
    rating: Optional[conint(ge=1, le=5)] = None # e.g., 1-5 star rating

class ReviewCreate(ReviewBase):
    pass # word_id will be path parameter, user_id from current_user

class ReviewUpdate(BaseModel):
    content: Optional[constr(min_length=1)] = None
    rating: Optional[conint(ge=1, le=5)] = None

class ReviewRead(ReviewBase):
    id: int
    word_id: int
    user_id: int # Or author_id
    author: Optional[UserRead] # Nested User information
    created_at: datetime.datetime

    class Config:
        orm_mode = True

# --- Word Schemas ---
class WordBase(BaseModel):
    title: constr(min_length=1, max_length=100)
    img_src: Optional[str] = None
    rating: Optional[confloat(ge=0)] = None # General rating, if applicable
    quote: Optional[str] = None # Definition, example, etc.
    # category_ids: Optional[List[int]] = None # For linking categories on create/update

class WordCreate(WordBase):
    # When creating a word, we might want to pass a list of category IDs
    category_ids: Optional[List[int]] = []

class WordUpdate(WordBase):
    title: Optional[constr(min_length=1, max_length=100)] = None # All fields optional for update
    img_src: Optional[str] = None
    rating: Optional[confloat(ge=0)] = None
    quote: Optional[str] = None
    category_ids: Optional[List[int]] = None # Allow updating categories

# For displaying a word, including its categories and reviews
class WordRead(WordBase):
    id: int
    created_at: datetime.datetime
    # Nested categories data
    categories: List[CategoryRead] = [] # Will hold CategoryRead objects
    # Nested reviews data
    reviews: List[ReviewRead] = []

    class Config:
        orm_mode = True

# Schema for Word list items (could be simpler than full WordRead if needed)
class WordList(WordRead): # For now, same as WordRead, can be customized
    pass


# Update forward references if any were used with string literals
# This is important if, for example, CategoryRead needed to reference WordRead.
# In this specific setup, UserRead and CategoryRead are imported directly.
# If WordRead were needed by them, we would do something like:
# CategoryRead.update_forward_refs()
# UserRead.update_forward_refs() # if it used WordRead

# For the current structure, explicit update_forward_refs might not be strictly
# necessary for WordRead itself as its nested types are fully defined or imported.
# However, it's good practice if you have complex interdependencies.

# Example: If CategoryRead had
# from ..category.schemas import CategoryRead # already imported
# CategoryRead.update_forward_refs(WordRead=WordRead)

# Our current models are:
# WordRead -> CategoryRead, ReviewRead
# ReviewRead -> UserRead
# These should resolve correctly with direct imports.
