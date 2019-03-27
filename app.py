from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
import os
import sys
import click

WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))

class Movie(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(60))
        year = db.Column(db.String(4))


# @app.cli.command()
# def forge():
#     """Generate fake data."""
#     db.create_all()
#     name = 'Mr Wu'
#     movies = [
#         {'title': 'My Neighbor Totoro', 'year': '1988'},
#         {'title': 'Dead Poets Society', 'year': '1989'},
#         {'title': 'A Perfect World', 'year': '1993'},
#         {'title': 'Leon', 'year': '1994'},
#         {'title': 'Mahjong', 'year': '1996'},
#         {'title': 'Swallowtail Butterfly', 'year': '1996'},
#         {'title': 'King of Comedy', 'year': '1999'},
#         {'title': 'Devils on the Doorstep', 'year': '1999'},
#         {'title': 'WALL-E', 'year': '2008'},
#         {'title': 'The Pork of Music', 'year': '2012'},
#     ]
#     user = User(name=name)
#     db.session.add(user)
#     for m in movies:
#         movie = Movie(title=m['title'], year=m['year'])  #按照数据库格式逐个加入数据库
#         db.session.add(movie)
#
#     db.session.commit()
#     click.echo('Done.')
#这个函数返回的变量（以字典键值对的形式）将会统一注入到每个模板的上下文环境中，因此可以直接在模板中使用
@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user=user)
#优化404页面
@app.errorhandler(404) # 传入要处理的错误代码
def page_not_found(e): # 接受异常对象作为参数
    return render_template('404.html'), 404  #返回模板和状态码

# 主页
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
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
        flash('Item update.')
        return redirect(url_for('index')) #重定向回主页

    return render_template('edit.html', movie=movie) # 传入被编辑的电影记录

@app.route('/movie/delete/<int:movie_id>', methods=['POST']) # 限定只接受 POST 请求
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id) #获取电影记录
    db.session.delete(movie) # 删除对于的记录
    db.session.commit() # 提交数据库会话
    flash('Item delete.')
    return redirect(url_for('index')) # 重定向回主页

if __name__ == "__main__":
    app.run()
