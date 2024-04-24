import json
import os

from flask import Blueprint, Response, request

from flaskr.setting import setting
from flaskr.utils import DataCheckUtils
from flaskr.utils.MapDownloadUtils import MapDownloadUtils

mapTile = Blueprint('mapTile', __name__, url_prefix='/')


@mapTile.route("/mapImg/<z>/<x>/<y>")
def mapImg(x, y, z):
    imgTypes = setting.global_imgTypes
    mapURLValue = setting.global_mapURLValue
    mapURLStyle = setting.global_mapURLStyle
    LOCAL_IMAGE_CACHE_DIR = "./map/" + mapURLValue + "/" + mapURLStyle + "/" + str(z) + "/" + str(x) + "/"
    # local_image_path = os.path.join(LOCAL_IMAGE_CACHE_DIR, str(y) + ".jpeg")

    for imgType in imgTypes:
        file_path = os.path.join(LOCAL_IMAGE_CACHE_DIR, str(y) + "." + imgType)
        if os.path.isfile(file_path) and os.path.exists(file_path):
            # 无论图片是从缓存读取还是刚下载完，都返回给客户端
            with open(file_path, 'rb') as img_file:
                img_data = img_file.read()

            # 设置正确的MIME类型
            mime_type = 'image/' + imgType  # 根据实际情况设置正确的图片MIME类型
            response = Response(img_data, mimetype=mime_type)
            # 返回图片数据
            return response

    savePath = None
    urlStr = None
    contentType = None

    mapUrl = DataCheckUtils.dataCheckNone(setting.global_mapURLValue)
    httpParameter = DataCheckUtils.dataCheckNone(setting.global_mapURLHttpParameter)
    httpProxies = setting.global_mapURLProxies
    httpHeaders = setting.global_mapURLHeaders
    # 下载地图前，参考用户设置的值
    if mapUrl.__eq__("googleMap"):
        lyrs = DataCheckUtils.dataCheckNone(setting.global_mapURLStyle,"s")
        hl = DataCheckUtils.dataCheckNone(setting.global_mapURLhl,"zh-CN")
        gl = DataCheckUtils.dataCheckNone(setting.global_mapURLgl,"cn")
        # httpParameter = None
        headers = httpHeaders
        proxies = httpProxies

        savePathGoogle, urlStrGoogle, contentTypeGoogle = MapDownloadUtils.googleMapDownload(x, y, z,lyrs=lyrs, hl=hl, gl=gl, httpParameter=httpParameter, headers=headers, proxies=proxies)
        savePath = savePathGoogle
        urlStr = urlStrGoogle
        contentType = contentTypeGoogle
    elif mapUrl.__eq__("AMap"):
        style = DataCheckUtils.dataCheckNone(setting.global_mapURLStyle,"6")
        headers = httpProxies
        proxies = httpHeaders
        savePathAMap, urlStrAMap, contentTypeAMap = MapDownloadUtils.AMapDownload(x, y, z,style=style, httpParameter=httpParameter, headers=headers, proxies=proxies)
        savePath = savePathAMap
        urlStr = urlStrAMap
        contentType = contentTypeAMap

    # 无论图片是从缓存读取还是刚下载完，都返回给客户端
    with open(savePath, 'rb') as img_file:
        img_data = img_file.read()

    # 设置正确的MIME类型
    mime_type = contentType  # 根据实际情况设置正确的图片MIME类型
    response = Response(img_data, mimetype=mime_type)

    # 返回图片数据
    return response


@mapTile.route("/mapTile/mapList", methods=['GET'])
def mapList():
    """
    返回现有的地图URL
    :return:
    """
    # 这个
    res = setting.global_mapList

    return res


@mapTile.route("/mapTile/setMapList", methods=['POST'])
def setMapList():
    """
    设置地图参数
    :return:
    """
    # 这个
    res = {
        "data": "",
        "code": 200
    }
    dataJson = request.get_json()
    mapUrl = dataJson["mapUrl"]
    mapType = dataJson["mapType"]
    httpParameter = dataJson["httpParameter"]
    httpProxies = dataJson["httpProxies"]
    httpHeaders = dataJson["httpHeaders"]
    glType = dataJson["glType"]
    hlType = dataJson["hlType"]

    setting.global_mapURLValue = mapUrl
    setting.global_mapURLStyle = mapType
    # &a=1&b=2
    setting.global_mapURLHttpParameter = httpParameter

    if DataCheckUtils.dataCheckNone(httpHeaders) is None:
        setting.global_mapURLHeaders = None
    else:
        try:
            setting.global_mapURLHeaders = json.loads(httpHeaders)
            if not isinstance(setting.global_mapURLHeaders, dict):
                setting.global_mapURLHeaders = None
                res["code"] = 400
                res["msg"] = '请求头参数错误，请设置为json格式；例如：{"Content-Type":"application/json"}'
                return res
        except json.JSONDecodeError:
            setting.global_mapURLHeaders = None
            res["code"] = 400
            res["msg"] = '请求头参数错误，请设置为json格式；例如：{"Content-Type":"application/json"}'
            return res

    if DataCheckUtils.dataCheckNone(httpProxies) is None:
        setting.global_mapURLProxies = None
    else:
        try:
            setting.global_mapURLProxies = json.loads(httpProxies)
            if not isinstance(setting.global_mapURLProxies, dict):
                setting.global_mapURLProxies = None
                res["code"] = 400
                res["msg"] = '代理端口参数错误，请设置为json格式；例如：{"http":"http://127.0.0.1:1234"}'
                return res
        except json.JSONDecodeError:
            setting.global_mapURLProxies = None
            res["code"] = 400
            res["msg"] = '代理端口参数错误，请设置为json格式；例如：{"http":"http://127.0.0.1:1234"}'
            return res

    # setting.global_mapURLHeaders = json.loads(httpHeaders)
    # setting.global_mapURLProxies = json.loads(httpProxies)
    setting.global_mapURLhl = glType
    setting.global_mapURLgl = hlType

    return res


@mapTile.route("/mapTile/currentMapSetting", methods=['GET'])
def currentMapSetting():
    """
    获得当前的 map 参数的设置
    :return:
    """
    res = {
        "data": {
            "mapURLValue": setting.global_mapURLValue,
            "mapURLStyle": setting.global_mapURLStyle,
            "mapURLhl": setting.global_mapURLhl,
            "mapURLgl": setting.global_mapURLgl,
            "mapURLHttpParameter": setting.global_mapURLHttpParameter,
            "mapURLHeaders": setting.global_mapURLHeaders,
            "mapURLProxies": setting.global_mapURLProxies
            # "mapURLHeaders": json.dump(setting.global_mapURLHeaders),
            # "mapURLProxies": json.dump(setting.global_mapURLProxies)
        }
    }

    return res



