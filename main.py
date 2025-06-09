from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from apps.home import router as home_router
from apps.movie import router as movie_router
from models import Base, engine

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(title="电影评论系统")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 注册路由
app.include_router(home_router)
app.include_router(movie_router)
