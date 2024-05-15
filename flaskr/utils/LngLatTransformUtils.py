import math


class LanLatTransformUtils(object):
    # 赤道半径

    ARC = 6371.393 * 1000

    @staticmethod
    def centralPoint_Angle_Distance(centralPointLan: float, centralPointLat: float, targetAngle: float,
                                    targetDist: float):
        """
            根据中心点经纬度，角度和距离计算目标点的经纬度
            距离为5000m内有20m的误差，距离越大误差越大，这是与arcgis.js 中的geodesicUtils.pointFromDistance方法对比的结果
            :param centralPointLan: 中心点的经度
            :param centralPointLat: 中心点的纬度
            :param targetAngle: 目标点的角度，范围：0-360
            :param targetDist:  目标点的距离(两点之间的直线距离)，单位：米
            :return: 目标点的经纬度
        """
        # 经纬度计算关系
        # 纬度计算只与地球半径（周长）有关；
        # 经度计算与地球半径（周长）及所处纬度相关。
        # 计算公式
        # 赤道半径：ARC = 6371.393 * 1000
        # 所求点到已知点的距离：垂直距离lath（所求点在已知点上方（北方）为正，否则为负），
        # 水平距离lngw（所求点在已知点右方（东方）为正，否则为负）
        res = {"lan": 0.0, "lat": 0.0}
        # 垂直距离lath（所求点在已知点上方（北方）为正，否则为负）
        lath = targetDist * math.fabs(math.cos(math.radians(targetAngle)))
        if (targetAngle > 90) and (targetAngle <= 270):
            lath = -lath
        lat = centralPointLat + lath / (LanLatTransformUtils.ARC * math.pi / 180)
        # 水平距离lngw（所求点在已知点右方（东方）为正，否则为负）
        lngw = targetDist * math.fabs(math.sin(math.radians(targetAngle)))
        if targetAngle > 180:
            lngw = -lngw
        lng = centralPointLan + lngw / (LanLatTransformUtils.ARC * math.cos(math.radians(lat)) * math.pi / 180)
        res["lan"] = lng
        res["lat"] = lat
        return res


if __name__ == '__main__':
    tempCentralPointLan = 112.935529
    tempCentralPointLat = 28.221944
    tempTargetAngle = 21.1
    tempTargetDist = 5250
    # 112.964484°E, 27.853213°N
    tempRes = LanLatTransformUtils.centralPoint_Angle_Distance(tempCentralPointLan, tempCentralPointLat,
                                                               tempTargetAngle, tempTargetDist)
    print(f"latitude: {tempRes['lat']} longitude:{tempRes['lan']}")
