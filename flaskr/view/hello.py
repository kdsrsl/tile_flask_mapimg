from flask import Blueprint, render_template

hello = Blueprint('hello', __name__, url_prefix='/')

@hello.route('/hello222')
def hello222():
    return 'Hello, World!'

@hello.route('/hello222333')
def hello222333():
    return 'hello222333, World!'

@hello.route('/')
def index():
    return render_template("index.html")