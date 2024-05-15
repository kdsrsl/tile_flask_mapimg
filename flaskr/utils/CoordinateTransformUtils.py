# -*- coding: utf-8 -*-
import math


class CoordinateTransformUtils:
    def __init__(self):
        pass

    # 设置常量
    pi = 3.141592653589793234  # π
    r_pi = pi * 3000.0 / 180.0
    la = 6378245.0  # 长半轴
    ob = 0.00669342162296594323  # 扁率

    # gcj02 -> bd09
    # lng为gcj02的经度
    # lat为gcj02的纬度
    # 返回值为转换后坐标的列表形式，[经度, 纬度]
    @staticmethod
    def gcj02_bd09(lon_gcj02, lat_gcj02):

        b = math.sqrt(lon_gcj02 * lon_gcj02 + lat_gcj02 * lat_gcj02) + 0.00002 * math.sin(
            lat_gcj02 * CoordinateTransformUtils.r_pi)
        o = math.atan2(lat_gcj02, lon_gcj02) + 0.000003 * math.cos(lon_gcj02 * CoordinateTransformUtils.r_pi)
        lon_bd09 = b * math.cos(o) + 0.0065
        lat_bd09 = b * math.sin(o) + 0.006
        return [lon_bd09, lat_bd09]

    # bd09 -> gcj02
    # lng为bd09的经度
    # lat为bd09的纬度
    # 返回值为转换后坐标的列表形式，[经度, 纬度]
    @staticmethod
    def bd09_gcj02(lon_bd09, lat_bd09):
        m = lon_bd09 - 0.0065
        n = lat_bd09 - 0.006
        c = math.sqrt(m * m + n * n) - 0.00002 * math.sin(n * CoordinateTransformUtils.r_pi)
        o = math.atan2(n, m) - 0.000003 * math.cos(m * CoordinateTransformUtils.r_pi)
        lon_gcj02 = c * math.cos(o)
        lat_gcj02 = c * math.sin(o)
        return [lon_gcj02, lat_gcj02]

    # wgs84 -> gcj02
    # lng为wgs84的经度
    # lat为wgs84的纬度
    # 返回值为转换后坐标的列表形式，[经度, 纬度]
    @staticmethod
    def wgs84_gcj02(lon_wgs84, lat_wgs84):
        if CoordinateTransformUtils.judge_China(lon_wgs84, lat_wgs84):  # 判断是否在国内
            return [lon_wgs84, lat_wgs84]
        tlat = CoordinateTransformUtils.transformlat(lon_wgs84 - 105.0, lat_wgs84 - 35.0)
        tlng = CoordinateTransformUtils.transformlng(lon_wgs84 - 105.0, lat_wgs84 - 35.0)
        rlat = lat_wgs84 / 180.0 * CoordinateTransformUtils.pi
        m = math.sin(rlat)
        m = 1 - CoordinateTransformUtils.ob * m * m
        sm = math.sqrt(m)
        tlat = (tlat * 180.0) / ((CoordinateTransformUtils.la * (1 - CoordinateTransformUtils.ob)) / (
                m * sm) * CoordinateTransformUtils.pi)
        tlng = (tlng * 180.0) / (CoordinateTransformUtils.la / sm * math.cos(rlat) * CoordinateTransformUtils.pi)
        lat_gcj02 = lat_wgs84 + tlat
        lon_gcj02 = lon_wgs84 + tlng
        return [lon_gcj02, lat_gcj02]

    # gcj02 -> wgs84
    # lng为gcj02的经度
    # lat为gcj02的纬度
    # 返回值为转换后坐标的列表形式，[经度, 纬度]
    @staticmethod
    def gcj02_wgs84(lon_gcj02, lat_gcj02):
        if CoordinateTransformUtils.judge_China(lon_gcj02, lat_gcj02):
            return [lon_gcj02, lat_gcj02]
        tlat = CoordinateTransformUtils.transformlat(lon_gcj02 - 105.0, lat_gcj02 - 35.0)
        tlng = CoordinateTransformUtils.transformlng(lon_gcj02 - 105.0, lat_gcj02 - 35.0)
        rlat = lat_gcj02 / 180.0 * CoordinateTransformUtils.pi
        m = math.sin(rlat)
        m = 1 - CoordinateTransformUtils.ob * m * m
        sm = math.sqrt(m)
        tlat = (tlat * 180.0) / ((CoordinateTransformUtils.la * (1 - CoordinateTransformUtils.ob)) / (
                m * sm) * CoordinateTransformUtils.pi)
        tlng = (tlng * 180.0) / (CoordinateTransformUtils.la / sm * math.cos(rlat) * CoordinateTransformUtils.pi)
        lat_wgs84 = 2 * lat_gcj02 - (lat_gcj02 + tlat)
        lon_wgs84 = 2 * lon_gcj02 - (lon_gcj02 + tlng)
        return [lon_wgs84, lat_wgs84]

    # wgs84 -> bd09
    # lng为wgs84的经度
    # lat为wgs84的纬度
    # 返回值为转换后坐标的列表形式，[经度, 纬度]
    @staticmethod
    def wgs84_bd09(lon_wgs84, lat_wgs84):
        # 先把wgs84坐标系的坐标转换为火星坐标系
        tmpList_gcj02 = CoordinateTransformUtils.wgs84_gcj02(lon_wgs84, lat_wgs84)
        # 然后把火星坐标系的坐标转换为百度坐标系
        return CoordinateTransformUtils.gcj02_bd09(tmpList_gcj02[0], tmpList_gcj02[1])

    # bd09 -> wgs84
    # lng为bd09的经度
    # lat为bd09的纬度
    # 返回值为转换后坐标的列表形式，[经度, 纬度]
    @staticmethod
    def bd09_wgs84(lon_bd09, lat_bd09):
        # 先把百度坐标系的经纬度转换为火星坐标系
        tmpList_gcj02 = CoordinateTransformUtils.bd09_gcj02(lon_bd09, lat_bd09)
        # 然后把火星坐标系的坐标转换为百度坐标系
        return CoordinateTransformUtils.gcj02_wgs84(tmpList_gcj02[0], tmpList_gcj02[1])

    # 经纬度计算功能类
    @staticmethod
    def transformlat(lon, lat):
        r = -100.0 + 2.0 * lon + 3.0 * lat + 0.2 * lat * lat + 0.1 * lon * lat + 0.2 * math.sqrt(math.fabs(lon))
        r += (20.0 * math.sin(6.0 * lon * CoordinateTransformUtils.pi) + 20.0 * math.sin(
            2.0 * lon * CoordinateTransformUtils.pi)) * 2.0 / 3.0
        r += (20.0 * math.sin(lat * CoordinateTransformUtils.pi) + 40.0 * math.sin(
            lat / 3.0 * CoordinateTransformUtils.pi)) * 2.0 / 3.0
        r += (160.0 * math.sin(lat / 12.0 * CoordinateTransformUtils.pi) + 320 * math.sin(
            lat * CoordinateTransformUtils.pi / 30.0)) * 2.0 / 3.0
        return r

    @staticmethod
    def transformlng(lon, lat):
        r = 300.0 + lon + 2.0 * lat + 0.1 * lon * lon + 0.1 * lon * lat + 0.1 * math.sqrt(math.fabs(lon))
        r += (20.0 * math.sin(6.0 * lon * CoordinateTransformUtils.pi) + 20.0 * math.sin(
            2.0 * lon * CoordinateTransformUtils.pi)) * 2.0 / 3.0
        r += (20.0 * math.sin(lon * CoordinateTransformUtils.pi) + 40.0 * math.sin(
            lon / 3.0 * CoordinateTransformUtils.pi)) * 2.0 / 3.0
        r += (150.0 * math.sin(lon / 12.0 * CoordinateTransformUtils.pi) + 300.0 * math.sin(
            lon / 30.0 * CoordinateTransformUtils.pi)) * 2.0 / 3.0
        return r

    # 简单判断坐标点是否在中国
    # 不在的话返回True
    # 在的话返回False
    @staticmethod
    def judge_China(lon, lat):
        if lon < 70 or lon > 140:
            return True
        if lat < 0 or lat > 55:
            return True
        return False

    # 坐标系转换的main函数
    # 0->gcj02
    # 1->wgs84
    # 2->bd09
    @staticmethod
    def main(lon, lat, fromCoord, toCoord):
        fromCoord = int(fromCoord)
        toCoord = int(toCoord)
        temp = []
        if fromCoord - toCoord != 0:
            # 新建变量
            # 进行坐标转换
            if fromCoord == 0 and toCoord == 1:
                temp = CoordinateTransformUtils.gcj02_wgs84(lon, lat)
            elif fromCoord == 0 and toCoord == 2:
                temp = CoordinateTransformUtils.gcj02_bd09(lon, lat)
            elif fromCoord == 1 and toCoord == 0:
                temp = CoordinateTransformUtils.wgs84_gcj02(lon, lat)
            elif fromCoord == 1 and toCoord == 2:
                temp = CoordinateTransformUtils.wgs84_bd09(lon, lat)
            elif fromCoord == 2 and toCoord == 0:
                temp = CoordinateTransformUtils.bd09_gcj02(lon, lat)
            elif fromCoord == 2 and toCoord == 1:
                temp = CoordinateTransformUtils.bd09_wgs84(lon, lat)
            return temp
        else:
            return [lon, lat]


if __name__ == '__main__':
    # 原坐标
    # lon = 116.50987588293626
    # lat = 39.82122830702036
    tempLon = 112.12905639951296
    tempLat = 28.549603702868932
    print("原坐标：", tempLon, ",", tempLat)
    # 将WGS-84坐标转换为GCJ-02
    result1 = CoordinateTransformUtils.wgs84_gcj02(tempLon, tempLat)
    print("WGS-84 -> GCJ-02：", result1)
    # 将GCJ-02坐标转换为WGS-84
    result2 = CoordinateTransformUtils.gcj02_wgs84(tempLon, tempLat)
    print("GCJ-02 -> WGS-84：", result2)
    # 将WGS-84坐标转换为BD-09
    result3 = CoordinateTransformUtils.wgs84_bd09(tempLon, tempLat)
    print("WGS-84 -> BD-09：", result3)
    # 将BD-09坐标转换为WGS-84
    result4 = CoordinateTransformUtils.bd09_wgs84(tempLon, tempLat)
    print("BD-09 -> WGS-84：", result4)
    # 将BD-09坐标转换为GCJ-02
    result5 = CoordinateTransformUtils.bd09_gcj02(tempLon, tempLat)
    print("BD-09 -> GCJ-02：", result5)
    # 将GCJ-02坐标转换为BD-09
    result6 = CoordinateTransformUtils.gcj02_bd09(tempLon, tempLat)
    print("GCJ-02 -> BD-09：", result6)
