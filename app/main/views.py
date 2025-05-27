from flask import render_template, request, current_app
from . import main
from ..models import Movie, Genre
from flask_sqlalchemy import SQLAlchemy
from .. import db

@main.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    
    # 构建查询
    query = Movie.query
    
    # 搜索条件
    if search:
        query = query.filter(Movie.title.like(f'%{search}%'))
    
    # 类型筛选
    if category:
        query = query.join(Movie.genres).join(Genre).filter(Genre.name == category)
    
    # 分页
    pagination = query.paginate(page=page, per_page=current_app.config['ITEMS_PER_PAGE'], error_out=False)
    movies = pagination.items
    
    # 获取所有类型用于筛选
    genres = Genre.query.all()
    
    return render_template('index.html',
                         movies=movies,
                         pagination=pagination,
                         search=search,
                         current_category=category,
                         genres=genres)