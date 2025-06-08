from pydantic import BaseModel, constr
from typing import Optional, List

# Base properties for a Category
class CategoryBase(BaseModel):
    name: constr(min_length=1, max_length=50)

# Properties to receive on category creation
class CategoryCreate(CategoryBase):
    pass

# Properties to receive on category update
class CategoryUpdate(CategoryBase):
    name: Optional[constr(min_length=1, max_length=50)] = None # All fields optional for update

# Properties to return to client
class CategoryRead(CategoryBase):
    id: int
    # If you want to show words associated with this category, you'd add a field like:
    # words: List['WordRead'] = [] # Forward reference, requires WordRead schema

    class Config:
        orm_mode = True

# If WordRead is needed for CategoryRead.words, and it's in another module,
# you might need to update forward refs after all schemas are defined.
# For now, keeping it simple. Example of how it could look with Word schema:
# from ..word.schemas import WordRead # Assuming word schemas are defined
# class CategoryReadWithWords(CategoryRead):
#     words: List[WordRead] = []
