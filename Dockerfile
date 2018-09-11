FROM ubuntu

MAINTAINER liangyuxin.02@gmail.com

# 设置时区
RUN apt-get install tzdata
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo "Asia/Shanghai" > /etc/timezone
RUN dpkg-reconfigure -f noninteractive tzdata

ENV CODE_DIR=/opt/MLService
ENV FLASK_APP=app
ENV FASTTEXT_MODEL_DIR=/opt/models/
ENV CONFIG_URL=http://127.0.0.1:9080/model_conf.json
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

VOLUME $CODE_DIR/logs
VOLUME $FASTTEXT_MODEL_DIR


COPY . $CODE_DIR

WORKDIR $CODE_DIR

RUN pip3 install -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com -r requirements.txt

CMD flask run --host=0.0.0.0 --port=8206
