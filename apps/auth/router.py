from fastapi import APIRouter, Depends, Request, HTTPException, Form, Cookie, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from models import get_db, User
from utils.security import generate_password_hash, verify_password
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Optional
import logging
from models.role_models import Role, Permission
import os
import shutil
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="templates", extensions=["jinja2.ext.do"])

# JWT配置
SECRET_KEY = "your-secret-key"  # 在生产环境中应该使用环境变量
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 头像上传配置
AVATAR_UPLOAD_DIR = "static/uploads/avatars"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB

# 确保上传目录存在
os.makedirs(AVATAR_UPLOAD_DIR, exist_ok=True)

def allowed_file(filename):
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        user = db.query(User).filter(User.username == username).first()
        return user
    except JWTError:
        return None

@router.get("/auth/login")
async def login_page(request: Request, current_user=Depends(get_current_user)):
    """登录页面"""
    return templates.TemplateResponse("auth/login.html", {"request": request, "current_user": current_user, "Permission": Permission})

@router.post("/auth/login")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """处理登录请求"""
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "error": "用户名或密码错误"
            },
            status_code=400
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    return response

@router.get("/auth/register")
async def register_page(request: Request, current_user=Depends(get_current_user)):
    """注册页面"""
    return templates.TemplateResponse("auth/register.html", {"request": request, "current_user": current_user, "Permission": Permission})

@router.post("/auth/register")
async def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    """处理注册请求"""
    # 验证密码
    if password != confirm_password:
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "error": "两次输入的密码不一致"
            },
            status_code=400
        )
    
    # 检查用户名是否已存在
    if db.query(User).filter(User.username == username).first():
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "error": "用户名已存在"
            },
            status_code=400
        )
    
    # 检查邮箱是否已存在
    if db.query(User).filter(User.email == email).first():
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "error": "邮箱已被注册"
            },
            status_code=400
        )
    
    # 查找默认角色
    default_role = db.query(Role).filter_by(default=True).first()
    
    # 创建新用户
    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
        role=default_role
    )
    db.add(user)
    db.commit()
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    return response

@router.get("/auth/logout")
async def logout():
    """处理登出请求"""
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("access_token")
    return response

@router.get("/auth/profile")
async def profile_page(request: Request, current_user=Depends(get_current_user)):
    if not current_user:
        return RedirectResponse(url="/auth/login", status_code=303)
    return templates.TemplateResponse(
        "auth/profile.html",
        {
            "request": request,
            "current_user": current_user,
            "Permission": Permission
        }
    )

@router.post("/auth/profile")
async def profile_update(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    phone: str = Form(""),
    bio: str = Form(""),
    password: str = Form(""),
    confirm_password: str = Form(""),
    avatar: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if not current_user:
        return RedirectResponse(url="/auth/login", status_code=303)
    
    # 检查用户名和邮箱唯一性
    if username != current_user.username and db.query(User).filter(User.username == username).first():
        return templates.TemplateResponse(
            "auth/profile.html",
            {
                "request": request,
                "current_user": current_user,
                "Permission": Permission,
                "error": "用户名已被使用"
            }
        )
    if email != current_user.email and db.query(User).filter(User.email == email).first():
        return templates.TemplateResponse(
            "auth/profile.html",
            {
                "request": request,
                "current_user": current_user,
                "Permission": Permission,
                "error": "邮箱已被使用"
            }
        )
    
    # 处理头像上传
    if avatar and avatar.filename:
        if not allowed_file(avatar.filename):
            return templates.TemplateResponse(
                "auth/profile.html",
                {
                    "request": request,
                    "current_user": current_user,
                    "Permission": Permission,
                    "error": "不支持的文件格式，请上传jpg、png或gif格式的图片"
                }
            )
        
        # 生成唯一的文件名
        file_ext = Path(avatar.filename).suffix
        new_filename = f"{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}{file_ext}"
        file_path = os.path.join(AVATAR_UPLOAD_DIR, new_filename)
        
        try:
            # 保存文件
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(avatar.file, buffer)
            
            # 更新用户头像URL
            current_user.avatar = f"/static/uploads/avatars/{new_filename}"
        except Exception as e:
            logger.error(f"头像上传失败: {str(e)}")
            return templates.TemplateResponse(
                "auth/profile.html",
                {
                    "request": request,
                    "current_user": current_user,
                    "Permission": Permission,
                    "error": "头像上传失败，请重试"
                }
            )
    
    # 更新用户信息
    current_user.username = username
    current_user.email = email
    current_user.phone = phone
    current_user.bio = bio
    
    # 密码修改
    if password:
        if password != confirm_password:
            return templates.TemplateResponse(
                "auth/profile.html",
                {
                    "request": request,
                    "current_user": current_user,
                    "Permission": Permission,
                    "error": "两次输入的密码不一致"
                }
            )
        current_user.password_hash = generate_password_hash(password)
    
    db.commit()
    return RedirectResponse(url="/auth/profile?success=1", status_code=303) 