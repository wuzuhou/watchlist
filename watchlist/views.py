# -*- coding: utf-8 -*-
from flask import render_template, request, url_for, redirect, flash
from flask_login import login_user, login_required, current_user, logout_user

from watchlist import app, db
from watchlist.models import User, Movie
from wtforms import Form, BooleanField, StringField, PasswordField, validators

# 主页及添加记录
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if not current_user.is_authenticated:  #如果当前用户未认证
            return redirect(url_for('index'))  # 重定向到主页
        #获取表单数据
        title = request.form.get('title')
        year = request.form.get('year')
        #验证数据
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('Invalid input.') # 显示错误
            return redirect(url_for('index')) # 重新定向主页
        # 保存表单数据到数据库
        movie = Movie(title=title, year=year) # 创建记录
        db.session.add(movie) # 添加到数据库会话
        db.session.commit() # 提交数据库会话
        flash('Item created.') # 显示成功创建的提示
        return redirect(url_for('index')) # 重定向回主页GET方法

    user = User.query.first()
    movies = Movie.query.all()
    return render_template('index.html', user=user, movies=movies)

#编辑电影条目
@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
@login_required
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    if request.method == 'POST':
        title = request.form['title']
        year = request.form['year']

        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('edit', movie_id=movie_id)) #重新定向到编辑页面

        movie.title= title #更新标题
        movie.year = year # 更新年份
        db.session.commit()
        flash('Item updated.')
        return redirect(url_for('index')) #重定向回主页

    return render_template('edit.html', movie=movie) # 传入被编辑的电影记录

#删除电影条目
@app.route('/movie/delete/<int:movie_id>', methods=['POST']) # 限定只接受 POST 请求
@login_required
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id) #获取电影记录
    db.session.delete(movie) # 删除对于的记录
    db.session.commit() # 提交数据库会话
    flash('Item deleted.')
    return redirect(url_for('index')) # 重定向回主页

#设置用户名字
@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']
        if not name or len(name) > 20:
            flash('Invalid input.')
            return redirect(url_for('settings'))


        user = User.query.first()
        user.name = name
        db.session.commit()
        flash('Settings updated.')
        return redirect(url_for('index'))

    return render_template('settings.html')

#用户登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']


        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))

        user = User.query.filter_by(username=username).first()
        if  username == user.username and user.validate_password(password):
            login_user(user) #登入用户
            flash('Login success.')
            return redirect(url_for('index'))

        flash('Invalid username or password.')
        return redirect(url_for('login'))
    else:
        return render_template('login.html')

#用户登出
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Goodbye.')
    return redirect(url_for('index'))

#用户注册
class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)# 自定义类 RegistrationForm，它继承了类Form的所有属性。实例化RegistrationForm（用参数request.form），并用form接住。
    if User.query.filter_by(email=form.email.data).first():
        flash('The email is already exist!')
        return redirect(url_for('login'))
    elif request.method == 'POST' and form.validate():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Thanks for registering')
        return redirect(url_for('login'))
    else:
        return render_template('register.html', form=form)
