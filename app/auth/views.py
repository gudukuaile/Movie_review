from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from ..models import User, Role
from .. import db

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        avatar = request.form.get('avatar', '')  # 头像URL
        phone = request.form.get('phone', '')    # 电话号码
        bio = request.form.get('bio', '')        # 个人简介
        
        if User.query.filter_by(username=username).first():
            flash('用户名已存在', 'danger')
            return redirect(url_for('auth.register'))
        
        # 获取默认用户角色
        user_role = Role.query.filter_by(default=True).first()
        
        user = User(
            username=username, 
            email=email, 
            avatar=avatar, 
            phone=phone, 
            bio=bio,
            role=user_role
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('注册成功！', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('登录成功！', 'success')
            return redirect(url_for('main.index'))
        
        flash('用户名或密码错误', 'danger')
    return render_template('auth/login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已成功退出登录', 'info')
    return redirect(url_for('main.index'))

@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        avatar = request.form.get('avatar', '')
        phone = request.form.get('phone', '')
        bio = request.form.get('bio', '')
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # 检查用户名是否已被其他用户使用
        if username != current_user.username and User.query.filter_by(username=username).first():
            flash('用户名已被使用', 'danger')
            return redirect(url_for('auth.profile'))
        
        # 检查邮箱是否已被其他用户使用
        if email != current_user.email and User.query.filter_by(email=email).first():
            flash('邮箱已被使用', 'danger')
            return redirect(url_for('auth.profile'))
        
        # 更新用户信息
        current_user.username = username
        current_user.email = email
        current_user.avatar = avatar
        current_user.phone = phone
        current_user.bio = bio
        
        # 如果提供了新密码，则更新密码
        if password:
            if password != confirm_password:
                flash('两次输入的密码不一致', 'danger')
                return redirect(url_for('auth.profile'))
            current_user.set_password(password)
        
        db.session.commit()
        flash('个人资料已更新', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/profile.html') 