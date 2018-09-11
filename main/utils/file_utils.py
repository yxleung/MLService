# -*- coding: UTF-8 -*-


import os
import requests
import progressbar
import requests.packages.urllib3 as urllib3
import main.config.logging_config as log

logger = log.getLogger()
urllib3.disable_warnings()


def count_lines(path):
    num = 0
    # with codecs.open(path, 'r', encoding='utf-8') as f:
    #     for line in f:
    #         num += 1
    cmd = "wc -l {}".format(path)
    result = os.popen(cmd).readlines()
    return result[0].split(' ')[0]


len_GB = pow(1024, 3)
len_MB = pow(1024, 2)
len_KB = 1024
unit_names = ["G", "M", "K", "byte"]


def get_file_size(length, min_unit='K'):
    g = int(length / len_GB)
    m = int((length % len_GB) / len_MB)
    k = int((length % len_MB) / len_KB)
    b = length % len_KB
    if g > 0:
        g = "{}G".format(g)
    else:
        g = ''
    if m > 0:
        m = "{}M".format(m)
    else:
        m = ''
    if k > 0:
        k = "{}K".format(k)
    else:
        k = ''
    if b > 0:
        b = "{}bytes".format(b)
    else:
        b = ''
    units = [g, m, k, b]
    idx = unit_names.index(min_unit)
    return " ".join(units[:idx + 1])


def download(url, dst_path):
    logger.info("download {} --> {}".format(url, dst_path))
    response = requests.request("GET", url, stream=True, data=None, headers=None, verify=False)
    total_length = int(response.headers.get("Content-Length"))
    logger.info("total length: {}".format(get_file_size(total_length, min_unit="byte")))
    with open(dst_path, 'wb') as f:
        widgets = ['Progress: ', progressbar.Percentage(), ' ',
                   progressbar.Bar(marker='#', left='[', right=']'),
                   ' ', progressbar.ETA(), ' ', progressbar.FileTransferSpeed()]
        pbar = progressbar.ProgressBar(widgets=widgets, maxval=total_length).start()
        current_len = 0
        for chunk in response.iter_content(chunk_size=1024 * 10):
            if chunk:
                f.write(chunk)
                f.flush()
            current_len += len(chunk)
            pbar.update(current_len)

        pbar.finish()


def download_text(url):
    logger.info("download_text {}".format(url))
    r = requests.get(url, verify=False)
    return r.content


def read_text(path):
    result = ''
    with open(path, 'r') as r:
        result = r.read()
    return result
