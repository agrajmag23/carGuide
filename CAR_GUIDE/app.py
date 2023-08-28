from flask import Flask, render_template, request
from main import *
app = Flask(__name__)


@app.route('/')
def hello_world():  # putflask application's code here
    return render_template('index.html')
# app.jinja_env.globals.update(search = search)

@app.route('/search')
def searchRequest():
    args = request.args
    print(args)
    q = args.get('q')
    print(q)
    res = search_query(q)
    return res


if __name__ == '__main__':
    app.run()
