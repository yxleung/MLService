# -*- coding: UTF-8 -*-
"""
    服务入口
"""
from flask import Flask, request, Response, render_template
import json
import datetime
import atexit
import main.config.logging_config as log
from main.config.ModelConfig import ModelConfig
from main.text.TextClassifier import TextClassifier
import main.utils.file_utils as futils

# logging init
log.init()
logger = log.getLogger()
logger.info('\n' + futils.read_text('banner'))
illegal_logger = log.getLogger(log.TEXT_LOGGER_ILLEGAL)
legal_logger = log.getLogger(log.TEXT_LOGGER_LEGAL)
webtest_logger = log.getLogger(log.TEXT_LOGGER_WEBTEST)

# model init
modelConfig = ModelConfig()
clf_model = TextClassifier(config=modelConfig.config)

# flash init
app = Flask(__name__)


@app.route('/barrage/classify', methods=['POST'])
def barrage_classify():
    param = request.get_data()
    if type(param) == bytes:
        param = param.decode()
    param = json.loads(param)
    text = param.get('text')
    req_id = param.get('id')
    business_name = param.get('business_name')
    business_code = param.get('business_code')
    room_id = param.get('room_id')
    result = {"id": req_id}
    t1 = datetime.datetime.now()
    try:
        tag, is_normal = clf_model.classify(text)
        result["isLegal"] = is_normal
        result["tag"] = tag
        result["code"] = 0
        log_content(text, tag, business_name, business_code, room_id)
    except Exception as e:
        result["code"] = 1
        logger.exception("calling BarrageClassifier error")
        result["msg"] = e
    finally:
        result["time"] = (datetime.datetime.now() - t1).total_seconds()
    s = json.dumps(result)
    logger.info("barrage_classify id->{}, text->{}; result->{}".format(req_id, text.encode('utf-8'), s))
    resp = Response(s)
    resp.headers['Content-Type'] = 'application/json;charset=UTF-8'
    return resp


@app.route('/barrage/batch/classify', methods=['POST'])
def batch_barrage_classify():
    param = request.get_data()
    if type(param) == bytes:
        param = param.decode()
    param = json.loads(param)
    data_list = param["list"]
    req_id = param.get('id')
    business_name = param.get('business_name')
    business_code = param.get('business_code')
    result = {"id": req_id}
    t1 = datetime.datetime.now()
    result_list = []
    list_size = 0
    result["code"] = 0
    try:
        if data_list:
            list_size = len(data_list)
            for item in data_list:
                result_list.append(clsf(business_name, business_code, item))

    except Exception as e:
        logger.exception("batch classify error")
        result["msg"] = str(e)
        result["code"] = 1
    finally:
        result["time"] = (datetime.datetime.now() - t1).total_seconds()
    result["list"] = result_list
    s = json.dumps(result)
    # print text
    logger.info("batch_barrage_classify id->{}, list_size->{}; time->{}".format(req_id, list_size, result["time"]))
    resp = Response(s)
    resp.headers['Content-Type'] = 'application/json;charset=UTF-8'
    return resp


@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    return render_template("index.html")


@app.route('/index', methods=['POST'])
def test_textClassify():
    text = request.form['text']
    tag, is_normal = clf_model.classify(text)
    result = {'text': text, 'tag': tag, 'is_normal': is_normal}
    webtest_logger.info("{}`{}".format(text, tag))
    return render_template("index.html", resp=result)


def clsf(business_name, business_code, item):
    text = item.get('text')
    req_id = item.get('id')
    room_id = item.get('room_id')
    result = {"id": req_id}
    tag, is_normal = clf_model.classify(text)
    result["isLegal"] = is_normal
    result["tag"] = tag
    log_content(text, tag, business_name, business_code, room_id)
    return result


def log_content(text, tag, business_name, business_code, room_id):
    if tag == 'illegal':
        illegal_logger.info(
            "{}`{}`{}`{}`{}".format(text, tag, business_name, business_code, room_id))
    if tag == 'legal':
        legal_logger.info("{}`{}`{}`{}`{}".format(text, tag, business_name, business_code, room_id))


def shutdown_hook():
    line = "============================="
    logger.info(line + '\n' + line + "\nSystem exit!!\n" + line)


atexit.register(shutdown_hook)

if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=False)
