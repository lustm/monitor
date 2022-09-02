FROM python:3.10.0-slim

COPY *.py /src/
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple flask psutil pynvml flask-apscheduler requests speedtest_cli
WORKDIR /src
ENV FLASK_APP=app.py
ENV LANG zh_CN.utf8
ENV  TIME_ZONE Asiz/Shanghai
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
EXPOSE 5000
CMD ["flask", "run", "-h", "0.0.0.0"]