# -- coding: utf-8 --
import json
from flask import Flask
from system import System

app = Flask(__name__)


@app.route('/')
def all_info():
    system = System()
    return json.dumps(system.obtain_all_info())


@app.route('/cpu')
def cpu_info():
    system = System()
    return json.dumps(system.obtain_cpu_info())


@app.route('/disk')
def disk_info():
    system = System()
    return json.dumps(system.obtain_disk_info())


@app.route('/memory')
def memory_info():
    system = System()
    return json.dumps(system.obtain_memory_info())


@app.route('/gpu')
def gpu_info():
    system = System()
    return json.dumps(system.obtain_gpu_info())


if __name__ == '__main__':
    app.run()
