import os

from flask import Flask

# create and configure the app
from flaskr.setting import setting
from flaskr.view import hello, mapTile

app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    SECRET_KEY='dev',
    DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
)

# 创建自定义地图上传文件夹
os.makedirs(setting.global_UPLOAD_CUSTOM_MAP_FOLDER, exist_ok=True)

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
