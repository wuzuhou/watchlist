from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager,login_user, login_required, UserMixin, current_user, logout_user
import os
import sys
import click

WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db') #数据库路径
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #关闭对模型修改的监控
app.config['SECRET_KEY'] = 'dev' #这个密钥主要用在cookie 和 session

db = SQLAlchemy(app)

class User(db.Model, UserMixin):   #用户认证用到 UserMixin
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    username = db.Column(db.String(20)) # 用户名
    password_hash = db.Column(db.String(128)) #密码散列值
      #生成密码散列值
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    #核对散列值与密码是否匹配
    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)

class Movie(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(60))
        year = db.Column(db.String(4))

# 虚拟数据并添加进数据库
@app.cli.command()
def forge():
    """Generate fake data."""
    db.create_all()
    name = 'henry'
    movies = [
        {'title': 'My Neighbor Totoro', 'year': '1988'},
        {'title': 'Dead Poets Society', 'year': '1989'},
        {'title': 'A Perfect World', 'year': '1993'},
        {'title': 'Leon', 'year': '1994'},
        {'title': 'Mahjong', 'year': '1996'},
        {'title': 'Swallowtail Butterfly', 'year': '1996'},
        {'title': 'King of Comedy', 'year': '1999'},
        {'title': 'Devils on the Doorstep', 'year': '1999'},
        {'title': 'WALL-E', 'year': '2008'},
        {'title': 'The Pork of Music', 'year': '2012'},
    ]
    user = User(name=name)
    db.session.add(user)
    for m in movies:
        movie = Movie(title=m['title'], year=m['year'])  #按照数据库格式逐个加入数据库
        db.session.add(movie)

    db.session.commit()
    click.echo('Done.')

# 重新生成数据库（清空数据）
@app.cli.command() # 绑定一个命令，可以在powershell里面用
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    """Initialize the database."""
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')

#生成管理员账户
@app.cli.command()
@click.option('--username', prompt=True, help='The username used to login.')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login.')
def admin(username, password):
    """Create user"""
    db.create_all()

    user = User.query.first()
    if user is not None:
        click.echo('Updating user...')
        user.username = username
        user.set_password(password)
    else:
        click.echo('Creating user...')
        user = User(username=username, name='Admin')
        user.set_password(password)
        db.session.add(user)
    db.session.commit()
    click.echo('Done.')


#初始化Flask-Login
login_manager = LoginManager(app) #实例化扩展类

@login_manager.user_loader
def load_user(user_id): #创建用户加载回调函数，接受用户ID作为对象
    user = User.query.get(int(user_id)) #用ID 作为 User 模型的主键查询对应的用户
    return user # 返回用户对象


#用户登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))

        user = User.query.first()
        # 验证用户名和密码是否一致
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

# 对未登录用户重定向到登录页面
login_manager.login_view = 'login'

#设置用户名字
@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']
        if not name or len(name) > 20:
            flash('Invalid input.')
            return redirect(url_for('settings'))

        current_user.name = name
        #current_user 会返回当前登录用户的数据记录对象
        #等同于下面的用法
        #user = User.query.first()
        #user.name = name
        db.session.commit()
        flash('Settings updated.')
        return redirect(url_for('index'))

    return render_template('settings.html')

# 这个函数返回的变量（以字典键值对的形式）将会统一注入到每个模板的上下文环境中，因此可以直接在模板中使用
@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user=user)

#优化404页面
@app.errorhandler(404) # 传入要处理的错误代码
def page_not_found(e): # 接受异常对象作为参数
    return render_template('404.html'), 404  #返回模板和状态码

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

if __name__ == "__main__":
    app.run()
