import minio
import time

from commonMethods_zhaozl_green.toolbox.Method_timeTrans import timeTrans


class MinioOperator:
    def __init__(self, host, port, user, pwd):
        self.host = host
        self.port = port
        self.user = user
        self.pwd = pwd
        self.minioObj = minio.Minio(endpoint=f"{host}:{port}", access_key=user, secret_key=pwd, secure=False)

    def getBucketNames(self):
        _obj = self.minioObj.list_buckets()
        return [item.name for item in _obj]

    def listContent(self, bucketName, recursive=True, prefix=None):
        _obj = self.minioObj.list_objects(bucketName, recursive=recursive, prefix=prefix)
        return [item.object_name for item in _obj]

    def getContent(self, bucketName, contentName):
        _obj = self.minioObj.get_object(bucketName, contentName)
        return _obj


def getTime():
    return timeTrans(unixTime=[int(time.time())], format='%Y-%m-%d %H:%M:%S').timeStr[0]