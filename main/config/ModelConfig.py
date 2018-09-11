# -*- coding: UTF-8 -*-

import os
import json
import main.utils.file_utils as futils
import main.config.logging_config as log


class ModelConfig:
    def __init__(self):
        self.logger = log.getLogger()
        self.config_url = os.environ.get("CONFIG_URL")
        self.config_path = os.path.join(os.getcwd(), 'model_conf.json')
        self.config = self.load_config()

    def load_config(self):
        if self.config_url:
            try:
                self.logger.info("Loading config from {}".format(self.config_url))
                text = futils.download_text(self.config_url)
                if text:
                    with open(self.config_path, 'w') as w:
                        self.logger.info("Write config to file {}".format(self.config_path))
                        if type(text) == bytes:
                            text = text.decode()
                        w.write(text)
                        w.flush()
                    try:
                        return json.loads(text)
                    except Exception:
                        self.logger.exception(
                            "Failed to convert config text to json object: {}\nTry to load local file {}".format(text,
                                                                                                                 self.config_path))
                        return self.load_local_config()
                else:
                    self.logger.info(
                        "Downloaded config is empty. Try to load local config file {}".format(self.config_path))
                    return self.load_local_config()
            except Exception:
                self.logger.exception(
                    "Failed to download config file from {}, try to load local file {}".format(self.config_url,
                                                                                               self.config_path))
                return self.load_local_config()
        else:
            self.logger.info(
                "Environment variable CONFIG_URL is empty, please set it correctly. Try to load local file {}".format(
                    self.config_path))
            return self.load_local_config()

    def load_local_config(self):
        self.logger.info("Loading local config file {}".format(self.config_path))
        with open(self.config_path, 'r') as r:
            text = r.read()
            if text:
                try:
                    return json.loads(text)
                except Exception as e:
                    self.logger.exception(
                        "Failed to convert local config text to json object: {}\n\n exit.".format(text))
                    exit(3)
            else:
                self.logger.error("Local config text is empty. Exit")
                exit(4)
