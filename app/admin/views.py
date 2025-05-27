from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from functools import wraps
from .. import db
from ..models import User, Movie, Role, Permission, Review
from . import admin

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                flash('您没有权限访问该页面。', 'error')
                return redirect(url_for('main.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    return permission_required(Permission.ADMIN)(f)

@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    user_count = User.query.count()
    movie_count = Movie.query.count()
    comment_count = db.session.query(db.func.count(Review.id)).scalar() if hasattr(db.session, 'query') else 0
    return render_template('admin/dashboard.html', 
                          user_count=user_count, 
                          movie_count=movie_count, 
                          comment_count=comment_count)

@admin.route('/users')
@login_required
@admin_required
def manage_users():
    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=current_app.config['ITEMS_PER_PAGE'], error_out=False)
    users = pagination.items
    return render_template('admin/users.html', users=users, pagination=pagination)

@admin.route('/user/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(id):
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        role_id = request.form.get('role')
        reset_password = request.form.get('reset_password')
        
        # 更新用户角色
        if role_id:
            role = Role.query.get(role_id)
            if role:
                user.role = role
                db.session.commit()
                flash('用户角色已更新。', 'success')
        
        # 重置用户密码
        if reset_password:
            user.set_password(reset_password)
            db.session.commit()
            flash('用户密码已重置。', 'success')
            
        return redirect(url_for('admin.manage_users'))
    
    roles = Role.query.all()
    return render_template('admin/edit_user.html', user=user, roles=roles)

@admin.route('/movies')
@login_required
@admin_required
def manage_movies():
    page = request.args.get('page', 1, type=int)
    pagination = Movie.query.order_by(Movie.created_at.desc() if hasattr(Movie, 'created_at') else Movie.id.desc()).paginate(
        page=page, per_page=current_app.config['ITEMS_PER_PAGE'], error_out=False)
    movies = pagination.items
    return render_template('admin/movies.html', movies=movies, pagination=pagination)

@admin.route('/movie/<int:id>/delete')
@login_required
@permission_required(Permission.MOVIE_DELETE)
def delete_movie(id):
    movie = Movie.query.get_or_404(id)
    db.session.delete(movie)
    db.session.commit()
    flash('电影已删除。', 'success')
    return redirect(url_for('admin.manage_movies'))

@admin.route('/reviews')
@login_required
@admin_required
def manage_reviews():
    page = request.args.get('page', 1, type=int)
    pagination = Review.query.order_by(Review.created_at.desc()).paginate(
        page=page, per_page=current_app.config['ITEMS_PER_PAGE'], error_out=False)
    reviews = pagination.items
    return render_template('admin/reviews.html', reviews=reviews, pagination=pagination)

@admin.route('/review/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_review(id):
    review = Review.query.get_or_404(id)
    if request.method == 'POST':
        content = request.form.get('content')
        rating = request.form.get('rating')
        
        if content:
            review.content = content
        
        if rating:
            try:
                review.rating = int(rating)
            except ValueError:
                flash('评分必须是数字。', 'danger')
                return redirect(url_for('admin.edit_review', id=review.id))
        
        db.session.commit()
        flash('评论已更新。', 'success')
        return redirect(url_for('admin.manage_reviews'))
    
    return render_template('admin/edit_review.html', review=review)

@admin.route('/review/<int:id>/delete')
@login_required
@admin_required
def delete_review(id):
    review = Review.query.get_or_404(id)
    db.session.delete(review)
    db.session.commit()
    flash('评论已删除。', 'success')
    return redirect(url_for('admin.manage_reviews'))