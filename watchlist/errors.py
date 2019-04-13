from flask import render_template

from watchlist import app

#优化400页面
@app.errorhandler(400) # 传入要处理的错误代码
def bad_request(e): # 接受异常对象作为参数
    return render_template('errors/400.html'), 400  #返回模板和状态码

#优化404页面
@app.errorhandler(404) # 传入要处理的错误代码
def page_not_found(e): # 接受异常对象作为参数
    return render_template('errors/404.html'), 404  #返回模板和状态码

#优化500页面
@app.errorhandler(500) # 传入要处理的错误代码
def internal_server_error(e): # 接受异常对象作为参数
    return render_template('errors/500.html'), 500  #返回模板和状态码
