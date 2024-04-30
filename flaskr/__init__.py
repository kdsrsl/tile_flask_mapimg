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


# 初始化读取自定义的瓦片图层
def readCustomMapType():
    folder_path = setting.global_UPLOAD_CUSTOM_MAP_FOLDER

    files = os.listdir(folder_path)
    for file in files:
        if os.path.isdir(os.path.join(folder_path, file)):  # 判断是否为文件夹
            setting.global_customMapTypes.append(file)
            # print(f"文件夹 {file}")


readCustomMapType()
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

if __name__ == '__main__':
    readCustomMapType()
