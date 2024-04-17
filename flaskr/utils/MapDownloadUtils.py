#!/usr/bin/python
# -*- coding: utf-8 -*-
import math
import random

import requests
import os


class MapDownloadUtils(object):
    """
    """

    @staticmethod
    def requestLoadImg(url, headers=None, proxies=None):
        """
        请求加载Img，返回响应字典 response
        :param url: 下载地址
        :param headers: 请求头
        :param proxies: 代理
        :return: response 响应字典
        """
        if headers is None:
            headers = {"Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8"}
        # 这里就看你自己是否需要开启代理
        # 此方法中的googleMap url 下载地址是需要开启代理的
        # if proxies is None:
        #     proxies = {
        #         "http": "http://127.0.0.1:1234",
        #         "https": "http://127.0.0.1:1234"
        #     }
        return requests.get(url, stream=True, headers=headers, proxies=proxies)

    @staticmethod
    def saveFileImg(savePath, fileResponse):
        """
        保存图片
        :param savePath: 保存路径
        :param fileResponse: response 字典
        :return: 无，可能会报无权限错误
        """
        pathIndex = savePath.rfind("/")
        os.makedirs(savePath[0:pathIndex], exist_ok=True)
        with open(savePath, 'wb') as img_file:
            for chunk in fileResponse.iter_content(chunk_size=1024):
                img_file.write(chunk)

    @staticmethod
    def googleMapDownload(x, y, z, lyrs="s", hl="zh-CN", gl="cn", httpParameter=None, headers=None, proxies=None):
        """
        下载google地图
        :param x: 坐标
        :param y: 坐标
        :param z: 坐标
        :param lyrs: 地图类型
        :param hl: host language(interface languages) 本地语言 ( zh-CN, zh-TW, en)
        :param gl: 国家码(country code) (cn,us)
        :param httpParameter: 可添加更多参数 &a=1&b=2&...
        :param headers: 请求头
        :param proxies: 代理
        :return:savePath(保存地图), urlStr(请求地址)
        """
        if httpParameter is None:
            httpParameter = "&lyrs=" + str(lyrs) + "&hl=" + str(hl) + "&gl=" + str(gl)
        else:
            httpParameter = httpParameter + "&lyrs=" + str(lyrs) + "&hl=" + str(hl) + "&gl=" + str(gl)

        return MapDownloadUtils.mapDownload(x, y, z, "googleMap", str(lyrs), httpParameter, headers, proxies)

    @staticmethod
    def AMapDownload(x, y, z, style="6", httpParameter=None, headers=None, proxies=None):
        """
        下载高德地图
        :param x: 坐标
        :param y: 坐标
        :param z: 坐标
        :param style: 地图类型
        :param httpParameter: 可添加更多参数 &a=1&b=2&...
        :param headers: 请求头
        :param proxies: 代理
        :return:savePath(保存地图), urlStr(请求地址)
        """
        if httpParameter is None:
            httpParameter = "&style=" + str(style)
        else:
            httpParameter = httpParameter + "&style=" + str(style)
        return MapDownloadUtils.mapDownload(x, y, z, "AMap", style, httpParameter, headers, proxies)

    @staticmethod
    def mapDownload(x, y, z, mapOrg, subFolderName=None, httpParameter=None, headers=None, proxies=None):
        """
        下载高德地图
        :param x: 坐标
        :param y: 坐标
        :param z: 坐标
        :param mapOrg: 地图提供商
        :param subFolderName: 保存文件夹子路径
        :param httpParameter: 可添加更多参数 a=1&b=2&...
        :param headers: 请求头
        :param proxies: 代理
        :return: savePath(保存地图), urlStr(请求地址)
        """

        savePath = ""
        urlStr = ""
        if mapOrg == "googleMap":
            serverNum = random.randint(0, 3)
            urlStr = f"https://mt{serverNum}.google.com/vt?x={x}&y={y}&z={z}" \
                .replace("{serverNum}", str(serverNum)).replace("{x}", str(x)) \
                .replace("{y}", str(y)).replace("{z}", str(z))
            if httpParameter is not None:
                urlStr += httpParameter
        elif mapOrg == "AMap":
            serverNum = random.randint(1, 4)
            urlStr = f"https://webst0{serverNum}.is.autonavi.com/appmaptile?x={x}&y={y}&z={z}" \
                .replace("{serverNum}", str(serverNum)).replace("{x}", str(x)) \
                .replace("{y}", str(y)).replace("{z}", str(z))
            if httpParameter is not None:
                urlStr += httpParameter

        response = MapDownloadUtils.requestLoadImg(urlStr, headers, proxies)

        # 检查响应状态码是否正常
        if response.status_code == 200:
            contentType = response.headers.get('content-type')
            fileSuffix = contentType.split("/")[1]
            if subFolderName is not None:
                savePath = mapOrg + "/" + str(subFolderName) + "/" + str(z) + "/" + str(x) + "/" + str(
                    y) + "." + fileSuffix
            else:
                savePath = mapOrg + "/" + "/" + str(z) + "/" + str(x) + "/" + str(y) + "." + fileSuffix
            savePath = os.path.join("./map/",savePath)

            MapDownloadUtils.saveFileImg(savePath, response)
            return savePath, urlStr, contentType
        else:
            print(f"response.status_code {response.status_code}")
            return savePath, urlStr, None

    # 经纬度转瓦片
    @staticmethod
    def lnglatToTile(lng, lat, zoom):
        """
        WGS-84 坐标系
        :param lng: 经度
        :param lat: 纬度
        :param zoom: 缩放
        :return:
        """
        tileX = int((lng + 180) / 360 * math.pow(2, zoom))
        tileY = int((1 - math.asinh(math.tan(math.radians(lat))) / math.pi) * math.pow(2, zoom - 1))
        return tileX, tileY

    # 瓦片转经纬度
    @staticmethod
    def tileToLnglat(tileX, tileY, zoom):
        """
        :param tileX: 
        :param tileY: 
        :param zoom: 
        :return: WGS-84 坐标系
        """
        lng = tileX / math.pow(2, zoom) * 360 - 180
        lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * tileY / math.pow(2, zoom)))))
        return lng, lat

    # 瓦片坐标的像素坐标转经纬度
    @staticmethod
    def pixelToLnglat(tileX, tileY, pixelX, pixelY, level):
        lng = (tileX + pixelX / 256) / math.pow(2, level) * 360 - 180
        lat = math.degrees(math.atan(math.sinh(math.pi - 2 * math.pi * (tileY + pixelY / 256) / math.pow(2, level))))
        return lng, lat


if __name__ == '__main__':
    x1 = 54658
    y1 = 26799
    z1 = 16
    savePath1, urlStr1 = MapDownloadUtils.googleMapDownload(x1, y1, z1)
    print(f"savePath1 {savePath1}")
    print(f"urlStr1 {urlStr1}")

    savePath1, urlStr1 = MapDownloadUtils.AMapDownload(x1, y1, z1)
    print(f"savePath1 {savePath1}")
    print(f"urlStr1 {urlStr1}")

    lng1 = 116.391135
    lat1 = 39.911290
    zoom1 = 11
    tileX1, tileY1 = MapDownloadUtils.lnglatToTile(lng1, lat1, zoom1)
    print(f"tileX1 {tileX1}")
    print(f"tileY1 {tileY1}")

    lng1, lat1 = MapDownloadUtils.tileToLnglat(tileX1, tileY1, zoom1)
    print(f"lng1 {lng1}")
    print(f"lat1 {lat1}")

    lng1 = 116.3671875
    lat1 = 40.044437584608566
    tileX11, tileY11 = MapDownloadUtils.lnglatToTile(lng1, lat1, zoom1)
    print(f"tileX11 {tileX11}")
    print(f"tileY11 {tileY11}")

    x1 = tileX1
    y1 = tileY1
    z1 = zoom1
    savePath1, urlStr1 = MapDownloadUtils.AMapDownload(x1, y1, z1)
    print(f"savePath1 {savePath1}")
    print(f"urlStr1 {urlStr1}")

    savePath1, urlStr1 = MapDownloadUtils.googleMapDownload(x1, y1, z1)
    print(f"savePath {savePath1}")
    print(f"urlStr {urlStr1}")
