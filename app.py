# -- coding: utf-8 --
import json
import platform
import time

import psutil
import pynvml
import requests
import speedtest
from flask import Flask
from flask_apscheduler import APScheduler

app = Flask(__name__)
# 推送服务器的接口地址
app.config["SERVER_URL"] = "http://localhost"
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

header = {
    "Content-Type": "application/json"
}


@app.route('/')
def index():
    return json.dumps(System.obtain_all_info())


@scheduler.task('interval', id='push_job', seconds=3, misfire_grace_time=900)
def push_job():
    """
    定时任务 推送系统信息
    :return: None
    """
    server_url = app.config.get('SERVER_URL')
    data = json.dumps(System.obtain_all_info())
    response = requests.post(url=server_url, data=data, headers=header)
    print(response.json())


class System:
    """
    系统信息类
    """

    def __init__(self):
        pass

    @staticmethod
    def obtain_all_info():
        return {
            'cpu': System.obtain_cpu_info(),
            'disk': System.obtain_disk_info(),
            'memory': System.obtain_memory_info(),
            'gpu': System.obtain_gpu_info(),
            'netFlow': System.obtain_net_flow()
        }

    @staticmethod
    def obtain_cpu_info():
        """
        获取电脑cpu信息
        :return: cpu
        """
        # 参数：interval ：扫描cpu的时间， percpu：默认为False，当为True时候返回每个cpu的使用率
        cpu = psutil.cpu_percent(interval=False, percpu=False)
        # 保留四位小数
        cpu = round(cpu / 100, 4)
        # cpu逻辑核心数
        cpu_count = psutil.cpu_count()
        # cpu物理核心数
        cpu_true_count = psutil.cpu_count(logical=False)
        # cpu频率
        cpu_freq = psutil.cpu_freq()
        info = {
            'cpuUsage': System.percentage_convert(cpu),
            'cpuCount': cpu_count,
            'cpuTrueCount': cpu_true_count,
            'cpuFreq': cpu_freq
        }
        return info

    @staticmethod
    def obtain_disk_info():
        """
        查看盘的使用情况
        :return: info2
        """
        disk_path = ''
        if platform.system().lower() == 'windows':
            disk_path = 'C:/'
        elif platform.system().lower() == 'linux':
            disk_path = '/'
        disk = psutil.disk_usage(disk_path)
        # 将信息写入一个字典
        info = {
            'total': System.hum_convert(disk[0]),
            'used': System.hum_convert(disk[1]),
            'free': System.hum_convert(disk[2]),
            'percent': System.percentage_convert(round(disk[3] / 100, 4)),
        }
        return info

    @staticmethod
    def obtain_memory_info():
        """
        获取电脑内存使用率
        :return: info
        """
        # 内存情况
        mem = psutil.virtual_memory()
        # 将内存情况放入一个字典，方便调用
        info = {
            'total': System.hum_convert(mem[0]),
            'free': System.hum_convert(mem[1]),
            'percent': System.percentage_convert(round(mem[2] / 100, 4)),
            'used': System.hum_convert(mem[3]),
        }
        return info

    @staticmethod
    def obtain_gpu_info():
        """
        获取gpu信息 只支持N卡
        :return: gpu_info_list
        """
        # 初始化
        pynvml.nvmlInit()
        # gpu驱动版本
        gpu_derive_info = pynvml.nvmlSystemGetDriverVersion()
        # 获取Nvidia GPU块数
        gpu_device_count = pynvml.nvmlDeviceGetCount()
        # print("GPU个数：", gpu_device_count)
        gpu_infos = []
        for i in range(gpu_device_count):
            # 获取GPU i的handle，后续通过handle来处理
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            # 通过handle获取GPU i的信息
            memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            # gpu名称
            gpu_name = str(pynvml.nvmlDeviceGetName(handle), encoding='utf-8')
            # gpu温度
            gpu_temperature = pynvml.nvmlDeviceGetTemperature(handle, 0)
            # gpu风扇转速
            # gpu_fan_speed = pynvml.nvmlDeviceGetFanSpeed(handle)
            # 供电水平
            gpu_power_state = pynvml.nvmlDeviceGetPowerState(handle)
            # gpu计算核心满速使用率
            gpu_util_rate = pynvml.nvmlDeviceGetUtilizationRates(handle).gpu
            # gpu内存读写满速使用率
            gpu_memory_rate = pynvml.nvmlDeviceGetUtilizationRates(handle).memory
            # 对pid的gpu消耗进行统计 获取所有GPU上正在运行的进程信息
            pid_all_info = pynvml.nvmlDeviceGetComputeRunningProcesses(handle)
            pid_infos = []
            for pid_info in pid_all_info:
                pid_user = psutil.Process(pid_info.pid).username()
                pid_info = {
                    'pid': pid_info.pid,
                    'pidUser': pid_user,
                    'usedGpuMemory': System.hum_convert(pid_info.usedGpuMemory)
                }
                pid_infos.append(pid_info)
            info = {
                'gpuName': gpu_name,
                'driverVersion': str(gpu_derive_info, encoding='utf-8'),
                'memoryTotal': System.hum_convert(memory_info.total),
                'memoryUsed': System.hum_convert(memory_info.used),
                'memoryFree': System.hum_convert(memory_info.free),
                'freeRate': System.percentage_convert(memory_info.free / memory_info.total),
                'usedRate': System.percentage_convert(memory_info.used / memory_info.total),
                'temperature': gpu_temperature,
                'powerSupplyLevel': gpu_power_state,
                'gpuUtilRate': gpu_util_rate,
                'gpuMemoryRate': gpu_memory_rate,
                'pidInfos': pid_infos
            }
            gpu_infos.append(info)
        # 最后关闭管理工具
        pynvml.nvmlShutdown()
        return gpu_infos

    @staticmethod
    def obtain_bandwidth():
        """
        获取系统网络带宽
        :return: info
        """
        # 创建实例对象
        test = speedtest.Speedtest()
        # 获取可用于测试的服务器列表
        test.get_servers()
        # 筛选出最佳服务器
        test.get_best_server()
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # 下载速度
        download_speed = int(test.download() / 1024 / 1024)
        # 上传速度
        upload_speed = int(test.download() / 1024 / 1024)
        info = {
            'downloadSpeed': str(download_speed) + "Mbps",
            'uploadSpeed': str(upload_speed) + "Mbps",
            'time': current_time
        }
        return info

    @staticmethod
    def obtain_net_flow():
        """
        系统当前流量
        :return: info
        """
        # 已发送的流量
        sent_before = psutil.net_io_counters().bytes_sent
        # 已接收的流量
        recv_before = psutil.net_io_counters().bytes_recv
        time.sleep(1)
        sent_now = psutil.net_io_counters().bytes_sent
        recv_now = psutil.net_io_counters().bytes_recv
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # 算出1秒后的差值
        sent = System.hum_convert(sent_now - sent_before)
        recv = System.hum_convert(recv_now - recv_before)
        info = {
            'download': sent,
            'upload': recv,
            'time': current_time
        }
        return info

    @staticmethod
    def hum_convert(value):
        units = ["B", "KB", "MB", "GB", "TB", "PB"]
        size = 1024.0
        for i in range(len(units)):
            if (value / size) < 1:
                return "%.2f%s" % (value, units[i])
            value = value / size

    @staticmethod
    def percentage_convert(value):
        return format(value, '.2%')


if __name__ == '__main__':
    app.run()
