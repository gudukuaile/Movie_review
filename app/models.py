from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from . import db, login_manager

class Permission:
    COMMENT = 1
    MOVIE_EDIT = 2
    MOVIE_DELETE = 4
    ADMIN = 8

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    @staticmethod
    def insert_roles():
        roles = {
            'User': [Permission.COMMENT],
            'Editor': [Permission.COMMENT, Permission.MOVIE_EDIT],
            'Admin': [Permission.COMMENT, Permission.MOVIE_EDIT, Permission.MOVIE_DELETE, Permission.ADMIN]
        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

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
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))        # 角色ID

    reviews = db.relationship('Review', backref='author', lazy=True)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == 'admin@example.com':
                self.role = Role.query.filter_by(name='Admin').first()
            else:
                self.role = Role.query.filter_by(default=True).first()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)
        
    def is_admin(self):
        return self.can(Permission.ADMIN)

class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False
        
    def is_admin(self):
        return False
        
login_manager.anonymous_user = AnonymousUser

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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 添加创建时间
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