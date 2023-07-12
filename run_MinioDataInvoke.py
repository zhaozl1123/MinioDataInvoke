from datetime import datetime, timedelta
import os
import json
import base64
import re
import numpy as np
import warnings, argparse

from flask import Flask, request
from flask_cors import CORS
from Method_MinioOperator import MinioOperator, getTime


app = Flask(__name__)
CORS(app, resources=r'/*')
mainServiceHost = os.environ.get("mainservicehost", "127.0.0.1")
mainServicePort = os.environ.get("mainserviceport", "8120")
minioHost = os.environ.get("miniohost", "127.0.0.1")
minioPort = os.environ.get("minioport", "9000")
minioUser = os.environ.get("miniouser", "minioadmin")
minioPwd = os.environ.get("miniopwd", "minioadmin")

# argParser = argparse.ArgumentParser()
# argParser.add_argument("--host", default=mainServiceHost, type=str, help="本服务IP地址，缺省 127.0.0.1", dest="host")
# argParser.add_argument("--port", default=int(mainServicePort), type=int, help="本服务端口号，缺省 8120", dest="port")
# argParser.add_argument("--miniohost", default=minioHost, type=str, help="minio服务IP地址，缺省 127.0.0.1", dest="miniohost")
# argParser.add_argument("--minioport", default=minioPort, type=int, help="minio服务端口号，缺省 9000", dest="minioport")
# argParser.add_argument("--miniouser", default=minioUser, type=str, help="minio用户名，缺省 minioadmin", dest="miniouser")
# argParser.add_argument("--miniopwd", default=minioPwd, type=str, help="minio密码，缺省 minioadmin", dest="miniopwd")
# arg = argParser.parse_args()
minioObj = MinioOperator(host=minioHost, port=str(minioPort), user=minioUser, pwd=minioPwd)

# mainServiceHost = os.environ.get("mainservicehost", "127.0.0.1")
# mainServicePort = os.environ.get("mainserviceport", "8120")
# minioHost = os.environ.get("miniohost", "127.0.0.1")
# minioPort = os.environ.get("minioport", "9000")
# minioUser = os.environ.get("miniouser", "minioadmin")
# minioPwd = os.environ.get("miniopwd", "minioadmin")
#
# # argParser = argparse.ArgumentParser()
# # argParser.add_argument("--host", default=mainServiceHost, type=str, help="本服务IP地址，缺省 127.0.0.1", dest="host")
# # argParser.add_argument("--port", default=int(mainServicePort), type=int, help="本服务端口号，缺省 8120", dest="port")
# # argParser.add_argument("--miniohost", default=minioHost, type=str, help="minio服务IP地址，缺省 127.0.0.1",
# #                        dest="miniohost")
# # argParser.add_argument("--minioport", default=minioPort, type=int, help="minio服务端口号，缺省 9000", dest="minioport")
# # argParser.add_argument("--miniouser", default=minioUser, type=str, help="minio用户名，缺省 minioadmin", dest="miniouser")
# # argParser.add_argument("--miniopwd", default=minioPwd, type=str, help="minio密码，缺省 minioadmin", dest="miniopwd")
# # arg = argParser.parse_args()
# minioObj = MinioOperator(host=minioHost, port=str(minioPort), user=minioUser, pwd=minioPwd)
# app.run(mainServiceHost, mainServicePort)


@app.route('/allBucketNames', methods=['GET'])
def get_all_buckets():
    global minioObj
    try:
        res = minioObj.getBucketNames()
        _json = {"bucketNames": res, "operationTime": getTime()}
        return json.dumps(_json, ensure_ascii=False)
    except Exception as e:
        _msg = f"无法访问minio服务，检查minio配置, " \
               f"HOST:{minioObj.host}  PORT:{minioObj.port}  USER:{minioObj.user}  PWD:{minioObj.pwd}"
        warnings.warn(_msg)
        warnings.warn(f"错误信息：{e}")
        _json = {"info": _msg, "operationTime": getTime()}
        return json.dumps(_json, ensure_ascii=False)


@app.route('/<bucketName>/contentNames', methods=['GET'])
def get_contents_in_bucket(bucketName):
    global minioObj
    try:
        res = minioObj.listContent(bucketName)
        res_suffixes = [item.split('.')[-1] for item in res]
        res_names = [item.split('.')[0] for item in res]
        return json.dumps(
                {"bucketName": bucketName, "contentNames": res_names, "contentSuffix": res_suffixes,  "operationTime": getTime()}, ensure_ascii=False
        )
    except Exception as e:
        _msg = f"无法访问minio服务，检查minio配置, " \
               f"HOST:{minioObj.host}  PORT:{minioObj.port}  USER:{minioObj.user}  PWD:{minioObj.pwd}"
        warnings.warn(_msg)
        warnings.warn(f"错误信息：{e}")
        _json = {"info": _msg, "operationTime": getTime()}
        return json.dumps(_json, ensure_ascii=False)


@app.route('/allBuckets/contentNames', methods=['GET'])
def get_contents_in_buckets():
    global minioObj
    try:
        bucketNames = minioObj.getBucketNames()
        res = {}
        for _bucketName in bucketNames:
            contentNames = minioObj.listContent(_bucketName, recursive=True)
            _res = {_bucketName: contentNames}
            res = {**res, **_res}
        return json.dumps({**res, **{"operationTime": getTime()}}, ensure_ascii=False)
    except Exception as e:
        _msg = f"无法响应，minio服务配置如下, " \
               f"HOST:{minioObj.host}  PORT:{minioObj.port}  USER:{minioObj.user}  PWD:{minioObj.pwd}"
        warnings.warn(_msg)
        warnings.warn(f"错误信息：{e}")
        _json = {"info": _msg, "operationTime": getTime()}
        return json.dumps(_json, ensure_ascii=False)


@app.route('/content/', methods=['GET'])
def get_content_in_bucket():
    global minioObj
    try:
        requestDict = request.args.to_dict()
        res = minioObj.getContent(requestDict["bucketName"], f"{requestDict['contentName']}.{requestDict['suffix']}")
        _suffix = requestDict["suffix"].lower()
        _strategy = {
            "txt": lambda: json.dumps(res.data.decode("utf-8"), ensure_ascii=False),
            "image": lambda: json.dumps(base64.b64encode(res.data).decode(), ensure_ascii=False),
        }
        if _suffix in ["txt"]:
            return _strategy[_suffix]()
        elif _suffix in ["jpg", "png"]:
            return _strategy["image"]()
        else:
            return json.dumps({"info": f"No file was found by info {{requestDict}}, check and try again.", "operationTime": getTime()})
    except Exception as e:
        _msg = f"无法响应，minio服务配置如下, " \
               f"HOST:{minioObj.host}  PORT:{minioObj.port}  USER:{minioObj.user}  PWD:{minioObj.pwd}"
        warnings.warn(_msg)
        warnings.warn(f"错误信息：{e}")
        _json = {"info": _msg, "operationTime": getTime()}
        return json.dumps(_json, ensure_ascii=False)


@app.route('/contentList/latest/', methods=['GET'])
def get_latest_content_list_in_buckets():
    global minioObj
    try:
        requestDict = request.args.to_dict()
        unitIndex = requestDict["unit"]
        res = {}
        if unitIndex != "0":
            try:
                _unitName = f"unit{requestDict['unit']}"
                res = get_latest_content_list_in_bucket(minioObj, _unitName)
            except Exception as e:
                pass
        else:
            index = 1
            while index <= 5:
                try:
                    _unitName = f"unit{index}"
                    _res = get_latest_content_list_in_bucket(minioObj, _unitName)
                    res = {**res, **_res}
                except Exception as e:
                    pass
                index += 1
        return json.dumps({"info": res, "operationTime": getTime()}, ensure_ascii=False)
    except Exception as e:
        _msg = f"无法响应，minio服务配置如下, " \
               f"HOST:{minioObj.host}  PORT:{minioObj.port}  USER:{minioObj.user}  PWD:{minioObj.pwd}"
        warnings.warn(_msg)
        warnings.warn(f"错误信息：{e}")
        _json = {"info": _msg, "operationTime": getTime()}
        return json.dumps(_json, ensure_ascii=False)


def get_latest_content_list_in_bucket(minioOperator, bucketName):
    retrievedData = []
    counter = 0
    _now = datetime.now()
    _deltaDate = timedelta(days=1)
    _dateList = _now.strftime("%Y-%m-%d").split("-")
    while (len(retrievedData) == 0) and (counter <= 30):
        prefer_day = "/".join(_dateList)
        retrievedData = minioOperator.listContent(bucketName, recursive=True, prefix=prefer_day)
        _dateList = (_now - _deltaDate).strftime("%Y-%m-%d").split("-")
        _now = _now - _deltaDate
        counter += 1
    _records = list(np.unique(re.findall("Record[0-9]{2,}", "".join([item.split("/")[3] for item in retrievedData]))))
    _maxRecordIndex = max([int(item.replace("Record", "")) for item in _records])
    res = []
    for item in retrievedData:
        _cache = f"Record{'0' if _maxRecordIndex < 10 else ''}{_maxRecordIndex}"
        if _cache in item:
            res.append(item)
    return {bucketName: res}


if __name__ == '__main__':
    # global minioObj
    #
    # mainServiceHost = os.environ.get("mainservicehost", "127.0.0.1")
    # mainServicePort = os.environ.get("mainserviceport", "8120")
    # minioHost = os.environ.get("miniohost", "127.0.0.1")
    # minioPort = os.environ.get("minioport", "9000")
    # minioUser = os.environ.get("miniouser", "minioadmin")
    # minioPwd = os.environ.get("miniopwd", "minioadmin")
    #
    # # argParser = argparse.ArgumentParser()
    # # argParser.add_argument("--host", default=mainServiceHost, type=str, help="本服务IP地址，缺省 127.0.0.1", dest="host")
    # # argParser.add_argument("--port", default=int(mainServicePort), type=int, help="本服务端口号，缺省 8120", dest="port")
    # # argParser.add_argument("--miniohost", default=minioHost, type=str, help="minio服务IP地址，缺省 127.0.0.1", dest="miniohost")
    # # argParser.add_argument("--minioport", default=minioPort, type=int, help="minio服务端口号，缺省 9000", dest="minioport")
    # # argParser.add_argument("--miniouser", default=minioUser, type=str, help="minio用户名，缺省 minioadmin", dest="miniouser")
    # # argParser.add_argument("--miniopwd", default=minioPwd, type=str, help="minio密码，缺省 minioadmin", dest="miniopwd")
    # # arg = argParser.parse_args()
    # minioObj = MinioOperator(host=minioHost, port=str(minioPort), user=minioUser, pwd=minioPwd)
    app.run(mainServiceHost, mainServicePort)