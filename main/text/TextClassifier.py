# -*- coding: UTF-8 -*-

import fastText
import os
import json
import re
import main.utils.file_utils as futils
import main.config.logging_config as log


class TextClassifier:
    def __init__(self, config):
        """
        initialize
        :param model_path: 如果为None，则读取环境变量FASTTEXT_MODEL_PATH的值
        """
        self.logger = log.getLogger()
        self.logger.info("Initializing classifier: \n{}".format(json.dumps(config)))
        self.model_path = os.path.join(os.environ.get("FASTTEXT_MODEL_DIR"), config["model_name"])
        self.model_url = config["model_url"]
        self.byte_length = config["byte_length"]
        self.check_model()
        self.logger.info("loading fasttext model from {}".format(self.model_path))
        self.clf = fastText.load_model(self.model_path)

    def check_model(self):
        if os.path.exists(self.model_path):
            file_size = os.path.getsize(self.model_path)
            if self.byte_length == file_size:
                self.logger.info( \
                    "model already exists and its size is the same as config which is {}({}), just use : {}" \
                        .format(self.byte_length, futils.get_file_size(self.byte_length), self.model_path))
                return
            else:
                self.logger.info( \
                    "model already exists but its size is {}({}) while {}({}) is configured, remove {} and re-download it." \
                        .format(file_size, futils.get_file_size(file_size), self.byte_length, \
                                futils.get_file_size(self.byte_length), self.model_path))
                os.remove(self.model_path)
                self.download_model()
                return
        else:
            self.logger.info("model doesn't exist at {}, download from {}".format(self.model_path, self.model_url))
            self.download_model()

    def download_model(self):
        try:
            futils.download(self.model_url, self.model_path)
            file_size = os.path.getsize(self.model_path)
            if self.byte_length == file_size:
                self.logger.info("Download OK!")
            else:
                self.logger.error("Download file length: {}({}) while {}({}) is configured, exit" \
                                  .format(file_size, futils.get_file_size(file_size), self.byte_length,
                                          futils.get_file_size(self.byte_length)))
                exit(2)
        except Exception as e:
            self.logger.exception("Failed to download model, exit!")
            exit(1)

    def classify(self, text, normal_tag_name="legal", split_tag="__label__"):
        # 过滤虎牙表情
        text = re.sub("\\/\\{ ?[a-zA-Z]{2}", "", text).strip()
        # 过滤全数字
        text = re.sub("^[0-9]+$", "", text).strip()
        # 过滤语气词
        text = re.sub("哈+|呵+", "", text).strip()
        # 过滤换行符
        text = re.sub("\n", "", text).strip()

        tag = normal_tag_name
        is_normal = True
        if not text == '':
            tags, probs = self.clf.predict(text)
            tag = tags[0].split(split_tag)[1]
            is_normal = True if normal_tag_name == tag else False
        return tag, is_normal
