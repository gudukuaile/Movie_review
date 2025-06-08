import os
from pydantic_settings import BaseSettings
from pydantic import EmailStr, AnyHttpUrl # Keep other pydantic imports
from dotenv import load_dotenv
from typing import List, Union

# 加载 .env 文件 (如果存在)
# .env 文件应该在项目的根目录下
# 例如: DATABASE_URL="sqlite:///./fastapi_refactor.db"
# SECRET_KEY="a_very_secret_key"
load_dotenv()

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_default_secret_key_here_please_change_it")
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    # SQLAlchemy 数据库 URL
    # 优先从环境变量读取，否则使用默认的 SQLite 数据库
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./fastapi_refactor.db")

    # 项目名称
    PROJECT_NAME: str = "FastAPI Refactored App"

    # 后端 CORS 源 (允许跨域请求的来源列表)
    # 例如: ["http://localhost", "http://localhost:8080", "https://yourdomain.com"]
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    # Pydantic 会自动尝试从环境变量中加载与属性同名的值
    # 例如，如果环境变量中有 SQLALCHEMY_DATABASE_URL，它会覆盖上面的默认值
    # 也可以通过 .env 文件来设置这些值

    # 管理员邮箱 (示例)
    FIRST_SUPERUSER_EMAIL: EmailStr = "admin@example.com"
    FIRST_SUPERUSER_PASSWORD: str = "admin123" # 生产环境中应使用更安全的密码或环境变量

    class Config:
        case_sensitive = True
        # 如果你在 .env 文件中定义了变量，Pydantic 会读取它们
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()
