from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import secrets
from apps.home import router as home_router
from apps.movie import router as movie_router
from apps.auth import router as auth_router
from apps.admin.router import router as admin_router
from models import Base, engine

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(title="电影评论系统")

# 生成一个安全的 secret key
SECRET_KEY = secrets.token_hex(32)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加 SessionMiddleware
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 注册路由
app.include_router(home_router)
app.include_router(movie_router)
app.include_router(auth_router)
app.include_router(admin_router)

import uvicorn

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)