from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return u'欢迎来到我的 Watchlist!'

@app.route('/hello')
def hola():
    return '<h1>hello Totoro!</h1><img src="http://helloflask.com/totoro.gif">'

if __name__ == "__main__":
    app.run()
