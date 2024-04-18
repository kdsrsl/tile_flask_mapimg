# -*- coding: utf-8 -*-
global_mapList = {
    "data": {
        "mapURLValue": ["googleMap","AMap"],
        "mapURLName": ["谷歌地图","高德地图"],
        "googleMap":{
            "mapTypeValue": ["s", "m", "t", "p", "y"],
            "mapTypeName": ["卫星图", "路线图", "地形图", "带标签的地形图", "带标签的卫星图"],
            # 本地语言
            "hlValue": ["zh-CN","en"],
            "hlName": ["中文","英文"],
            # 国家码
            "glValue": ["cn", "us"],
            "glName": ["cn", "us"],
            "httpParameter":"",
            "headers": "",
            "proxies": ""
        },
        "AMap": {
            "mapTypeValue": ["6", "7", "8"],
            "mapTypeName": ["卫星图", "矢量图", "路网图"],
            "httpParameter": "",
            "headers": "",
            "proxies": ""
        }
    }
}

global_mapURLValue = global_mapList["data"]["mapURLValue"][1]
global_mapURLStyle = global_mapList["data"][global_mapURLValue]["mapTypeValue"][0]
global_mapURLhl = None
global_mapURLgl = None
global_mapURLHttpParameter = "&a=1&b=2"
global_mapURLHeaders = None  # {"Content-Type":"application/json"}
global_mapURLProxies = {"http": "http://127.0.0.1:1234"}


