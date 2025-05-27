from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db, login_manager

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)  # 用户名
    email = db.Column(db.String(120), unique=True, nullable=False)     # 邮箱
    password_hash = db.Column(db.String(128))                         # 密码哈希值
    avatar = db.Column(db.String(255))                                # 头像URL
    phone = db.Column(db.String(20))                                  # 电话号码
    bio = db.Column(db.Text)                                          # 个人简介
    created_at = db.Column(db.DateTime, default=datetime.utcnow)      # 注册时间

    reviews = db.relationship('Review', backref='author', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Genre(db.Model):
    __tablename__ = 'genres'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    movies = db.relationship('MovieGenre', back_populates='genre')

class MovieGenre(db.Model):
    __tablename__ = 'movie_genres'
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.id'), nullable=False)
    movie = db.relationship('Movie', back_populates='genres')
    genre = db.relationship('Genre', back_populates='movies')

class Movie(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String(255))         # 电影详情链接
    img_src = db.Column(db.String(255))      # 图片链接
    title = db.Column(db.String(100))        # 影片中文名
    rating = db.Column(db.Float)             # 评分
    judge_num = db.Column(db.Integer)        # 评价人数
    quote = db.Column(db.Text)               # 简介
    director = db.Column(db.String(100))     # 导演
    actors = db.Column(db.String(200))       # 主演
    year = db.Column(db.String(10))          # 年份
    country = db.Column(db.String(50))       # 国家
    duration = db.Column(db.String(20))      # 片长
    genre = db.Column(db.String(50))         # 类型（用于迁移）
    genres = db.relationship('MovieGenre', back_populates='movie')
    reviews = db.relationship('Review', backref='movie', lazy=True)

class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False) 