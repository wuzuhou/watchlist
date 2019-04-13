# -*- coding: utf-8 -*-
import os
import sys

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev' #这个密钥主要用在cookie 和 session
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(os.path.dirname(app.root_path), 'data.db') #数据库路径
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #关闭对模型修改的监控

db = SQLAlchemy(app)
login_manager = LoginManager(app) #实例化扩展类

@login_manager.user_loader
def load_user(user_id): #创建用户加载回调函数，接受用户ID作为对象
    from watchlist.models import User
    user = User.query.get(int(user_id)) #用ID 作为 User 模型的主键查询对应的用户
    return user # 返回用户对象

# 对未登录用户重定向到登录页面
login_manager.login_view = 'login'

@app.context_processor
def inject_user():
    from watchlist.models import User
    user = User.query.first()
    return dict(user=user)

from watchlist import views, errors, commands
