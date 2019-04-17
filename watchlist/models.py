# -*- coding: utf-8 -*-
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from watchlist import db

class User(db.Model, UserMixin):   #用户认证用到 UserMixin
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    username = db.Column(db.String(20)) # 用户名
    password_hash = db.Column(db.String(128)) #密码散列值
    # tall = db.Column(db.Integer)
    # nickname = db.Column(db.String(20))
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
