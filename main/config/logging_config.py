# -*- coding: UTF-8 -*-

import os
import logging.config
import logging

APP_LOGGER = 'applogger'
TEXT_LOGGER_ILLEGAL = 'textlogger.illegal'
TEXT_LOGGER_LEGAL = 'textlogger.legal'
TEXT_LOGGER_WEBTEST = 'textlogger.webtest'



def init():
    project_path = os.getcwd()
    logs_dir = os.path.join(project_path, 'logs')
    logging_conf = os.path.join(project_path, 'logging.conf')
    # 判断logs文件夹是否存在
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    logging.config.fileConfig(logging_conf)

def getLogger(logger_name=APP_LOGGER):
    return logging.getLogger(logger_name)
