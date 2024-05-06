import json
import os

from flask import Blueprint, Response, request, flash

from flaskr.setting import setting
from flaskr.utils import DataCheckUtils
from flaskr.utils.MapDownloadUtils import MapDownloadUtils
from flaskr.utils import MyFileUtils

mapTile = Blueprint('mapTile', __name__, url_prefix='/')


@mapTile.route("/mapImg/upload", methods=["POST"])
def upload():
    res = {
        "code": 500,
        "data": "",
        "msg": ""
    }
    # 是不是一个file，是否包含mapFile文件字段
    if 'mapFile' not in request.files:
        flash('No file part')
        res["code"] = 400
        res["msg"] = "请上传的文件"
        return res
    mapFile = request.files['mapFile']
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if mapFile.filename == '':
        flash('No selected file')
        res["code"] = 400
        res["msg"] = "请上传的文件"
        return res
    # 检查是否为压缩包
    if mapFile and MyFileUtils.allowed_file(mapFile.filename, setting.global_zipTypes):
        # 检查文件大小200MB
        if mapFile.content_length > setting.global_file_max_length:
            res["code"] = 413
            res["msg"] = "文件不能超过200MB"
            return res

        # 解决中文名称文件上传问题
        filename = MyFileUtils.secure_filename(mapFile.filename)
        # filename = secure_filename(mapFile.filename)
        zipPath = os.path.join(setting.global_UPLOAD_CUSTOM_MAP_FOLDER, filename).__str__()
        zipPathAbs = os.path.abspath(zipPath)
        # mapFile.save(os.path.join(setting.global_UPLOAD_CUSTOM_MAP_FOLDER, filename))
        # 保存上传的压缩文件
        mapFile.save(zipPathAbs)

        isExistImgFile, firstImgFilePath = MyFileUtils.checkMapZipFileIncludeImg(zipPathAbs)
        delParentPath = ""  # 需要删除的父文件夹
        strPath = ""
        if isExistImgFile:
            firstImgFilePaths = firstImgFilePath.split("/")
            if len(firstImgFilePaths) == 3:
                firstImgFilePaths.insert(0, filename.split(".")[0])
            else:  # 4层，说明有多余的层数，我们需要删除
                delParentPath = firstImgFilePaths[0]

            # 获得合并瓦片类型
            uploadMapType = request.form.get("uploadMapType")
            # 新增加自定义地图类型
            if uploadMapType == '':
                if firstImgFilePaths[0] in setting.global_customMapTypes:
                    # 已经存在这个文件夹,这个时候要重命名了
                    indexTemp = 2
                    while firstImgFilePaths[0] + "(" + str(indexTemp) + ")" in setting.global_customMapTypes:
                        indexTemp = indexTemp + 1
                    firstImgFilePaths[0] = firstImgFilePaths[0] + "(" + str(indexTemp) + ")"
                # 解压
                strPath = MyFileUtils.mapFileUnZip2(zipPathAbs, firstImgFilePaths[0])
                # 添加到瓦片类型列表中
                setting.global_customMapTypes.append(firstImgFilePaths[0])
            # 合并到已有数据类型
            else:
                if uploadMapType in setting.global_customMapTypes:
                    mergePath = os.path.join(setting.global_UPLOAD_CUSTOM_MAP_FOLDER, uploadMapType).__str__()
                    mergePathAbs = os.path.abspath(mergePath)
                    # 解压
                    strPath = MyFileUtils.mapFileUnZip(zipPathAbs, firstImgFilePaths[0], mergePathAbs)
                else:
                    res["code"] = 400
                    res["msg"] = "请上传正确的瓦片资源压缩包"
                    return res
            if len(delParentPath) != 0:
                # 删除多余的层数
                MyFileUtils.childFoldersUpParentPath(strPath + "\\" + delParentPath, True, True)
            res["code"] = 200
            res["msg"] = "上传成功"
            return res
        else:
            # 错误
            res["code"] = 400
            res["msg"] = "请上传正确的瓦片资源压缩包"
            return res

    return res


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
    # urlStr = None
    contentType = None

    mapUrl = DataCheckUtils.dataCheckNone(setting.global_mapURLValue)
    httpParameter = DataCheckUtils.dataCheckNone(setting.global_mapURLHttpParameter)
    httpProxies = setting.global_mapURLProxies
    httpHeaders = setting.global_mapURLHeaders
    # 下载地图前，参考用户设置的值
    if mapUrl.__eq__("googleMap"):
        lyrs = DataCheckUtils.dataCheckNone(setting.global_mapURLStyle, "s")
        hl = DataCheckUtils.dataCheckNone(setting.global_mapURLhl, "zh-CN")
        gl = DataCheckUtils.dataCheckNone(setting.global_mapURLgl, "cn")
        # httpParameter = None
        headers = httpHeaders
        proxies = httpProxies

        savePathGoogle, urlStrGoogle, contentTypeGoogle = MapDownloadUtils.googleMapDownload \
            (x, y, z, lyrs=lyrs, hl=hl,
             gl=gl,
             httpParameter=httpParameter,
             headers=headers,
             proxies=proxies)
        savePath = savePathGoogle
        # urlStr = urlStrGoogle
        contentType = contentTypeGoogle
    elif mapUrl.__eq__("AMap"):
        style = DataCheckUtils.dataCheckNone(setting.global_mapURLStyle, "6")
        headers = httpProxies
        proxies = httpHeaders
        savePathAMap, urlStrAMap, contentTypeAMap = MapDownloadUtils.AMapDownload(x, y, z, style=style,
                                                                                  httpParameter=httpParameter,
                                                                                  headers=headers, proxies=proxies)
        savePath = savePathAMap
        # urlStr = urlStrAMap
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
