# ALLOWED_EXTENSIONS = {'.txt', '.pdf', '.png', '.jpg', '.jpeg', '.gif'}
import os
import re
import shutil
import tarfile
import unicodedata
import zipfile

import rarfile as rarfile
import werkzeug


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
    :return: boolean 是否符合地图瓦片资源文件夹结构; firstImgPath 第一个文件夹图片
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


def mapFileUnZip(mapFilePath: str, firstImgPath: str, unzipPath=None):
    """
    解压地图文件
    :param mapFilePath: 地图资源压缩包文件路径(最好是绝对路径)
    :param firstImgPath: 第一个地图资源的路径
    :param unzipPath: 解压存放路径
    :return: 解压文件夹根目录
    """
    # [".tar", ".tgz", ".zip", ".rar"]
    pathIndex = mapFilePath.rindex("\\")
    pathStr = mapFilePath[0:pathIndex]
    filename = mapFilePath[pathIndex + 1:]
    filenamePrefix = filename.split(".")[0]

    if unzipPath is None:
        if len(firstImgPath.split("/")) == 3:
            # 创建根目录文件夹
            pathStr = pathStr + "\\" + filenamePrefix
            os.makedirs(pathStr, exist_ok=True)
        shutil.unpack_archive(mapFilePath, pathStr)
        return pathStr
    else:
        shutil.unpack_archive(mapFilePath, unzipPath)
        return unzipPath


def mapFileUnZip2(mapFilePath: str, firstImgPath: str):
    """
    解压地图文件
    :param mapFilePath: 地图资源压缩包文件路径(最好是绝对路径)
    :param firstImgPath: 第一个地图资源的路径
    :return: 解压文件夹根目录
    """
    # [".tar", ".tgz", ".zip", ".rar"]
    pathIndex = mapFilePath.rindex("\\")
    pathStr = mapFilePath[0:pathIndex]
    # filename = mapFilePath[pathIndex + 1:]

    # 创建根目录文件夹
    pathStr = pathStr + "\\" + firstImgPath
    os.makedirs(pathStr, exist_ok=True)
    # 解压
    shutil.unpack_archive(mapFilePath, pathStr)
    return pathStr


def childFoldersCopyParentFolders(parentFoldersPath: str, childFoldersName: str, isDelChildFolders: bool):
    """
    将childFoldersName文件夹移动到与父类同级，isDelChildFolders 旧的子文件夹
    :param parentFoldersPath: 父文件夹
    :param childFoldersName: 子文件夹名称
    :param isDelChildFolders: 是否删除 旧的子文件夹
    :return:
    """
    # 设置父文件夹路径和子文件夹名称
    # parent_folder_path = '/path/to/parent/folder'
    # child_folder_name = 'child_folder'
    parent_folder_path = parentFoldersPath
    child_folder_name = childFoldersName

    # 构建子文件夹的完整路径
    child_folder_path = os.path.join(parent_folder_path, child_folder_name)

    # 确保子文件夹存在
    assert os.path.exists(child_folder_path), "Child folder does not exist"

    # 提升子文件夹级别，这里假设提升后的目标路径是父文件夹的同级路径
    new_child_folder_path = os.path.dirname(parent_folder_path)
    new_child_folder_path = os.path.join(new_child_folder_path, child_folder_name)

    # 如果目标路径已存在子文件夹，先删除
    if os.path.exists(new_child_folder_path):
        shutil.rmtree(new_child_folder_path)

    # 移动子文件夹到新的路径
    # shutil.move(child_folder_path, new_child_folder_path)
    shutil.copytree(child_folder_path, new_child_folder_path)

    if isDelChildFolders:
        # 删除原本的子文件夹
        shutil.rmtree(parent_folder_path+"\\"+child_folder_name)


def childFoldersUpParentPath(parentFoldersPath: str, isDelChildFolders: bool, isDelParentFolders: bool):
    # 设置父文件夹路径和子文件夹名称
    parent_folder_path = parentFoldersPath
    files = os.listdir(parent_folder_path)
    for file in files:
        childFoldersCopyParentFolders(parent_folder_path, file, isDelChildFolders)

    if isDelParentFolders:
        # 删除原本的文件夹
        shutil.rmtree(parentFoldersPath)


def secure_filename(filename: str) -> str:
    r"""Pass it a filename and it will return a secure version of it.  This
    filename can then safely be stored on a regular file system and passed
    to :func:`os.path.join`.  The filename returned is an ASCII only string
    for maximum portability.

    On windows systems the function also makes sure that the file is not
    named after one of the special device files.

    >>> secure_filename("My cool movie.mov")
    'My_cool_movie.mov'
    >>> secure_filename("../../../etc/passwd")
    'etc_passwd'
    >>> secure_filename('i contain cool \xfcml\xe4uts.txt')
    'i_contain_cool_umlauts.txt'

    The function might return an empty filename.  It's your responsibility
    to ensure that the filename is unique and that you abort or
    generate a random filename if the function returned an empty one.

    .. versionadded:: 0.5

    :param filename: the filename to secure
    """
    filename = unicodedata.normalize("NFKD", filename)
    filename = filename.encode("utf8", "ignore").decode("utf8")   # 编码格式改变

    for sep in os.path.sep, os.path.altsep:
        if sep:
            filename = filename.replace(sep, " ")
    _filename_ascii_add_strip_re = re.compile(r'[^A-Za-z0-9_\u4E00-\u9FBF\u3040-\u30FF\u31F0-\u31FF.-]')
    filename = str(_filename_ascii_add_strip_re.sub('', '_'.join(filename.split()))).strip('._')             # 添加新规则

    # on nt a couple of special files are present in each folder.  We
    # have to ensure that the target file is not such a filename.  In
    # this case we prepend an underline
    if (
        os.name == "nt"
        and filename
        and filename.split(".")[0].upper() in werkzeug.utils._windows_device_files
    ):
        filename = f"_{filename}"

    return filename
