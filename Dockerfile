FROM python:3.10.0-slim

COPY *.py /src/
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple flask psutil pynvml flask-apscheduler requests speedtest_cli
WORKDIR /src
ENV FLASK_APP=app.py
EXPOSE 5000
CMD ["flask", "run", "-h", "0.0.0.0"]