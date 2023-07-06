import os
import json
import base64
import warnings, argparse

from flask import Flask, request
from Method_MinioOperator import MinioOperator, getTime


app = Flask(__name__)

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
        return json.dumps(
            {"bucketName": bucketName, "contentNames": res, "operationTime": getTime()}, ensure_ascii=False
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


if __name__ == '__main__':
    # mainServiceHost = os.environ.get("mainservicehost", "127.0.0.1")
    # mainServicePort = os.environ.get("mainserviceport", "8120")
    # minioHost = os.environ.get("miniohost", "127.0.0.1")
    # minioPort = os.environ.get("minioport", "9000")
    # minioUser = os.environ.get("miniouser", "minioadmin")
    # minioPwd = os.environ.get("miniopwd", "minioadmin")
    #
    # argParser = argparse.ArgumentParser()
    # argParser.add_argument("--host", default=mainServiceHost, type=str, help="本服务IP地址，缺省 127.0.0.1", dest="host")
    # argParser.add_argument("--port", default=int(mainServicePort), type=int, help="本服务端口号，缺省 8120", dest="port")
    # argParser.add_argument("--miniohost", default=minioHost, type=str, help="minio服务IP地址，缺省 127.0.0.1", dest="miniohost")
    # argParser.add_argument("--minioport", default=minioPort, type=int, help="minio服务端口号，缺省 9000", dest="minioport")
    # argParser.add_argument("--miniouser", default=minioUser, type=str, help="minio用户名，缺省 minioadmin", dest="miniouser")
    # argParser.add_argument("--miniopwd", default=minioPwd, type=str, help="minio密码，缺省 minioadmin", dest="miniopwd")
    # arg = argParser.parse_args()
    # minioObj = MinioOperator(host=arg.miniohost, port=str(arg.minioport), user=arg.miniouser, pwd=arg.miniopwd)
    # app.run(arg.host, arg.port)
    mainServiceHost = os.environ.get("mainservicehost", "127.0.0.1")
    mainServicePort = os.environ.get("mainserviceport", "8120")
    minioHost = os.environ.get("miniohost", "127.0.0.1")
    minioPort = os.environ.get("minioport", "9000")
    minioUser = os.environ.get("miniouser", "minioadmin")
    minioPwd = os.environ.get("miniopwd", "minioadmin")

    # argParser = argparse.ArgumentParser()
    # argParser.add_argument("--host", default=mainServiceHost, type=str, help="本服务IP地址，缺省 127.0.0.1", dest="host")
    # argParser.add_argument("--port", default=int(mainServicePort), type=int, help="本服务端口号，缺省 8120", dest="port")
    # argParser.add_argument("--miniohost", default=minioHost, type=str, help="minio服务IP地址，缺省 127.0.0.1",
    #                        dest="miniohost")
    # argParser.add_argument("--minioport", default=minioPort, type=int, help="minio服务端口号，缺省 9000", dest="minioport")
    # argParser.add_argument("--miniouser", default=minioUser, type=str, help="minio用户名，缺省 minioadmin", dest="miniouser")
    # argParser.add_argument("--miniopwd", default=minioPwd, type=str, help="minio密码，缺省 minioadmin", dest="miniopwd")
    # arg = argParser.parse_args()
    minioObj = MinioOperator(host=minioHost, port=str(minioPort), user=minioUser, pwd=minioPwd)
    app.run(mainServiceHost, mainServicePort)