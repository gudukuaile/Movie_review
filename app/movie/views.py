from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from . import movie
from ..models import Movie, Review, Genre, MovieGenre, Permission
from .. import db
from functools import wraps

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                flash('您没有权限执行此操作。', 'error')
                return redirect(url_for('main.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@movie.route('/<int:id>')
def detail(id):
    movie = Movie.query.get_or_404(id)
    # 获取未删除的评论
    reviews = Review.query.filter_by(movie_id=id).order_by(Review.created_at.desc()).all()
    return render_template('movie/detail.html', movie=movie, reviews=reviews)

@movie.route('/add', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.MOVIE_EDIT)
def add():
    if request.method == 'POST':
        title = request.form['title']
        director = request.form['director']
        actors = request.form['actors']
        year = request.form['year']
        country = request.form.get('country', '')
        duration = request.form.get('duration', '')
        description = request.form['description']
        
        poster = request.files['poster']
        if poster and poster.filename:
            filename = secure_filename(poster.filename)
            poster.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            poster_path = f'uploads/{filename}'
        else:
            poster_path = 'default.jpg'
        
        # 创建新电影
        movie = Movie(
            title=title,
            director=director,
            actors=actors,
            year=year,
            country=country,
            duration=duration,
            quote=description,
            img_src=poster_path
        )
        
        db.session.add(movie)
        db.session.commit()
        
        # 处理电影类型
        genres = request.form.getlist('genres')
        for genre_name in genres:
            genre = Genre.query.filter_by(name=genre_name).first()
            if not genre:
                genre = Genre(name=genre_name)
                db.session.add(genre)
                db.session.commit()
            
            movie_genre = MovieGenre(movie_id=movie.id, genre_id=genre.id)
            db.session.add(movie_genre)
        
        db.session.commit()
        flash('电影添加成功！', 'success')
        return redirect(url_for('movie.detail', id=movie.id))
    
    # 获取所有可用的电影类型
    all_genres = Genre.query.all()
    return render_template('movie/add.html', all_genres=all_genres)

@movie.route('/<int:id>/review', methods=['POST'])
@login_required
def add_review(id):
    movie = Movie.query.get_or_404(id)
    content = request.form['content']
    rating = request.form['rating']
    
    review = Review(
        content=content,
        rating=rating,
        author=current_user,
        movie=movie
    )
    
    db.session.add(review)
    db.session.commit()
    flash('评价提交成功！', 'success')
    return redirect(url_for('movie.detail', id=id))

@movie.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.MOVIE_EDIT)
def edit_movie(id):
    movie = Movie.query.get_or_404(id)
    if request.method == 'POST':
        movie.title = request.form.get('title')
        movie.director = request.form.get('director')
        movie.actors = request.form.get('actors')
        movie.year = request.form.get('year')
        movie.country = request.form.get('country')
        movie.duration = request.form.get('duration')
        movie.quote = request.form.get('quote')
        movie.img_src = request.form.get('img_src')
        
        # 处理电影类型
        # 首先清除现有的类型关联
        MovieGenre.query.filter_by(movie_id=movie.id).delete()
        
        # 添加新的类型关联
        genres = request.form.getlist('genres')
        for genre_name in genres:
            genre = Genre.query.filter_by(name=genre_name).first()
            if not genre:
                genre = Genre(name=genre_name)
                db.session.add(genre)
                db.session.commit()
            
            movie_genre = MovieGenre(movie_id=movie.id, genre_id=genre.id)
            db.session.add(movie_genre)
        
        try:
            db.session.commit()
            flash('电影信息已更新', 'success')
            return redirect(url_for('movie.detail', id=movie.id))
        except Exception as e:
            db.session.rollback()
            flash('更新失败，请重试', 'error')
    
    # 获取所有可用的电影类型
    all_genres = Genre.query.all()
    return render_template('movie/edit_movie.html', 
                         movie=movie, 
                         all_genres=all_genres)

@movie.route('/delete/<int:id>')
@login_required
@permission_required(Permission.MOVIE_DELETE)
def delete_movie(id):
    movie = Movie.query.get_or_404(id)
    db.session.delete(movie)
    db.session.commit()
    flash('电影已删除。', 'success')
    return redirect(url_for('main.index'))