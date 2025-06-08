from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base # Removed
from sqlalchemy.orm import sessionmaker
from core.config import settings # 稍后创建 config.py
from models.base import Base # Import Base from models.base

# SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db" # 示例 SQLite URL
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db" # 示例 PostgreSQL URL

engine = create_engine(
    settings.DATABASE_URL,
    # connect_args={"check_same_thread": False} # 仅 SQLite 需要
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = declarative_base() # Removed, Base is now imported

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 初始化数据库表的函数 (可选，Alembic 更常用)
def init_db():
    # 在这里导入所有定义了 Base 的模型，以便 Base 能找到它们
    # import models.user_models, models.word_models, models.category_models 等
    # Base.metadata.create_all(bind=engine)
    pass
