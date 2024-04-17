def dataCheckNone(data,defaultData=None):
    """
    检测data数据是否为none,并且给默认值
    :param data:  源数据
    :param defaultData:  默认值，如果源数据为none或者‘’时，返回默认值
    :return:
    """
    if data is not None and len(data) > 0:
        defaultData = data

    return defaultData
