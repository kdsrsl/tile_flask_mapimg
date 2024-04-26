# ALLOWED_EXTENSIONS = {'.txt', '.pdf', '.png', '.jpg', '.jpeg', '.gif'}
import os
import shutil
import tarfile
import zipfile

import rarfile as rarfile


def allowed_file(filename, allowedExtensions):
    """
    检测文件后缀是否为allowed_extensions数组中的类型
    :param filename:  文件名
    :param allowedExtensions:  许可文件后缀数组
    :return: boolean  是否许可
    """
    return '.' in filename and \
           "." + filename.rsplit('.', 1)[1].lower() in allowedExtensions


def checkMapZipFileIncludeImg(mapZipFile, allowedImgExtensions=None):
    """
    检查压缩包中是否有图片资源，
    且图片资源的层数为 map/z/x/y.jpg 或者 z/x/y.jpg
    :param mapZipFile: 地图图片资源压缩包路径
    :param allowedImgExtensions: 许可的图片资源后缀数组
    :return: boolean 是否符合地图瓦片资源文件夹结构
    """
    if allowedImgExtensions is None:
        allowedImgExtensions = ["jpeg", "png", "jpg", "gif", "webp"]

    firstImgPath = ""
    filePathList = []
    if mapZipFile.endswith(".tar") or mapZipFile.endswith(".tgz"):
        with tarfile.open(mapZipFile, "r") as fileStream:
            # filePathList = fileStream.getmembers()
            for member in fileStream.getmembers():
                filePathList.append(member.name)
            fileStream.close()
    elif mapZipFile.endswith(".zip"):
        with zipfile.ZipFile(mapZipFile, "r") as fileStream:
            filePathList = fileStream.namelist()
            fileStream.close()
    elif mapZipFile.endswith(".rar"):
        with rarfile.RarFile(mapZipFile, "r") as fileStream:
            filePathList = fileStream.namelist()
            fileStream.close()

    for filename in filePathList:
        if len(firstImgPath) > 0:
            break
        for imgSuffix in allowedImgExtensions:
            if filename.endswith("." + imgSuffix):
                firstImgPath = filename
                # print(f"checkMapZipFileIncludeImg Loaded image {filename}")
                break

    if len(firstImgPath.split("/")) == 3 or len(firstImgPath.split("/")) == 4:
        return True, firstImgPath

    return False, firstImgPath


def mapFileUnZip(mapFile: str, firstImgPath: str, unzipPath=None):
    """
    解压地图文件
    :param mapFile: 地图资源压缩包文件路径(最好是绝对路径)
    :param firstImgPath: 第一个地图资源的路径
    :param unzipPath: 解压存放路径
    :return: 解压文件夹根目录
    """
    # [".tar", ".tgz", ".zip", ".rar"]
    pathIndex = mapFile.rindex("\\")
    pathStr = mapFile[0:pathIndex]
    filename = mapFile[pathIndex + 1:]
    filenamePrefix = filename.split(".")[0]
    if len(firstImgPath.split("/")) == 3:
        # 创建根目录文件夹
        pathStr = pathStr+"\\"+filenamePrefix
        os.makedirs(pathStr, exist_ok=True)

    if unzipPath is None:
        shutil.unpack_archive(mapFile, pathStr)
        return pathStr
    else:
        shutil.unpack_archive(mapFile, unzipPath)
        return unzipPath


# if __name__ == "__main__":
#     mapFilePath = "D:\MapTileDownload/331看看.zip"
#     # mapFilePath = "D:\MapTileDownload/331看看/34324123是是是.zip"
#     mapFilePath = os.path.abspath(mapFilePath)
#     isMapFile, nameFile = checkMapZipFileIncludeImg(mapFilePath)
#     if isMapFile:
#         unzipPathAdd = mapFileUnZip(mapFilePath, nameFile)
#         print(f"解压目录 {unzipPathAdd}")
#     else:
#         print(f"错误，不是地图瓦片 {mapFilePath}")
