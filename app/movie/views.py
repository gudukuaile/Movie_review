from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from . import movie
from ..models import Movie, Review, Genre, MovieGenre
from .. import db

@movie.route('/<int:id>')
def detail(id):
    movie = Movie.query.get_or_404(id)
    return render_template('movie/detail.html', movie=movie)

@movie.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        title = request.form['title']
        director = request.form['director']
        actors = request.form['actors']
        year = request.form['year']
        description = request.form['description']
        category = request.form['category']
        
        poster = request.files['poster']
        if poster:
            filename = secure_filename(poster.filename)
            poster.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            poster_path = f'uploads/{filename}'
        else:
            poster_path = 'default.jpg'
        
        movie = Movie(
            title=title,
            director=director,
            actors=actors,
            year=year,
            quote=description,  # 保存到quote字段，与模型一致
            genre=category,     # 保存到genre字段，与模型一致
            img_src=poster_path # 保存到img_src字段，与模板一致
        )
        
        db.session.add(movie)
        db.session.commit()
        flash('电影添加成功！')
        return redirect(url_for('main.index'))
    
    return render_template('movie/add.html')

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
    flash('评价提交成功！')
    return redirect(url_for('movie.detail', id=id))

@movie.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
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
            movie_genre = MovieGenre(movie=movie, genre=genre)
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