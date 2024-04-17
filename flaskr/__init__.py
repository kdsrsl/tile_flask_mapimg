import os

from flask import Flask

# create and configure the app
from flaskr.view import hello, mapTile

app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    SECRET_KEY='dev',
    DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
)

# ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

# a simple page that says hello
# @app.route('/hello')
# def hello():
#     return 'Hello, World!'

app.register_blueprint(hello.hello)
app.register_blueprint(mapTile.mapTile)
