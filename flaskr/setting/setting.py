# -*- coding: utf-8 -*-
# 设置最大上传大小为200MB
global_file_max_length = 200 * 1024 * 1024

# 上传压缩包中需要的图片类型
global_imgTypes = ["jpeg", "png", "jpg", "gif", "webp"]
# 上传压缩包类型
# global_zipTypes = [".tar", ".tgz", ".zip", ".rar"]
global_zipTypes = [".zip", ".tar", ".tgz"]
# global_customMapTypes = ["test1", "test2", "test3"]
global_customMapTypes = []

global_UPLOAD_CUSTOM_MAP_FOLDER = "./map/customMap"

global_mapList = {
    "data": {
        "mapURLValue": ["googleMap", "AMap", "customMap"],
        "mapURLName": ["谷歌地图", "高德地图", "自定义地图"],
        "googleMap": {
            "mapTypeValue": ["s", "m", "t", "p", "y"],
            "mapTypeName": ["卫星图", "路线图", "地形图", "带标签的地形图", "带标签的卫星图"],
            # 本地语言
            "hlValue": ["zh-CN", "en"],
            "hlName": ["中文", "英文"],
            # 国家码
            "glValue": ["cn", "us"],
            "glName": ["cn", "us"],
            "httpParameter": "",
            "headers": "",
            "proxies": ""
        },
        "AMap": {
            "mapTypeValue": ["6", "7", "8"],
            "mapTypeName": ["卫星图", "矢量图", "路网图"],
            "httpParameter": "",
            "headers": "",
            "proxies": ""
        },
        "customMap": {
            # "alreadyMapTypes": ["test1", "test2", "test3"],  # 这个以用户上传的压缩包命名
            "mapTypeValue": global_customMapTypes,  # 这个以用户上传的压缩包命名
            "zipTypes": global_zipTypes,  # 这个以用户上传的压缩包命名
            # 所以它的地址是：
            # mapURLValue="customMap"
            # mapURLStyle=alreadyMapType+"/"+mapCustomURLStyle
            # alreadyMapType=
            # mapCustomURLStyle=
            # "./map/customMap/test1/" + str(z) + "/" + str(x) + "/"
        }
    }
}

global_mapURLValue = global_mapList["data"]["mapURLValue"][1]
global_mapURLStyle = global_mapList["data"][global_mapURLValue]["mapTypeValue"][2]
global_mapURLhl = None
global_mapURLgl = None
global_mapURLHttpParameter = "&a=1&b=2"
global_mapURLHeaders = None  # {"Content-Type":"application/json"}
global_mapURLProxies = {"http": "http://127.0.0.1:1087"}
# global_customAlreadyMapType = ""
# global_customAlreadyMapTypes = ["test1", "test2", "test3"]
