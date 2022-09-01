# -- coding: utf-8 --

import psutil
import pynvml
import platform


class System:
    # 查询单位 1024*1024 => MB
    unit = None
    # 扫描cpu的时间
    cpu_scan_interval = None

    def __init__(self, cpu_scan_interval=False, unit=1024 * 1024):
        self.cpu_scan_interval = cpu_scan_interval
        self.unit = unit

    def obtain_all_info(self):
        return {
            'cpu': self.obtain_cpu_info(),
            'disk': self.obtain_disk_info(),
            'memory': self.obtain_memory_info(),
            'gpu': self.obtain_gpu_info()
        }

    def obtain_cpu_info(self):
        """
        获取电脑cpu信息
        :return: cpu
        """
        # 参数：interval ：扫描cpu的时间， percpu：默认为False，当为True时候返回每个cpu的使用率
        cpu = psutil.cpu_percent(interval=self.cpu_scan_interval)
        # 保留四位小数
        cpu = round(cpu / 100, 4)
        # cpu逻辑核心数
        cpu_count = psutil.cpu_count()
        # cpu物理核心数
        cpu_true_count = psutil.cpu_count(logical=False)
        # cpu频率
        cpu_freq = psutil.cpu_freq()
        info = {
            'cpuUsage': cpu,
            'cpuCount': cpu_count,
            'cpuTrueCount': cpu_true_count,
            'cpuFreq': cpu_freq
        }
        return info

    def obtain_disk_info(self):
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
            'total': disk[0] / self.unit,
            'used': disk[1] / self.unit,
            'free': disk[2] / self.unit,
            'percent': round(disk[3] / 100, 4),
        }
        return info

    def obtain_memory_info(self):
        """
        获取电脑内存使用率
        :return: info
        """
        # 内存情况
        mem = psutil.virtual_memory()
        # 将内存情况放入一个字典，方便调用
        info = {
            'total': mem[0] / self.unit,
            'free': mem[1] / self.unit,
            'percent': round(mem[2] / 100, 4),
            'used': mem[3] / self.unit,
        }
        return info

    def obtain_gpu_info(self):
        """
        获取gpu信息 只支持N卡
        :return: gpu_info_list
        """
        # 初始化
        pynvml.nvmlInit()
        # gpu驱动版本
        gpu_derive_info = pynvml.nvmlSystemGetDriverVersion()
        print("Drive版本: ", str(gpu_derive_info, encoding='utf-8'))  # 显示驱动信息
        # 获取Nvidia GPU块数
        gpu_device_count = pynvml.nvmlDeviceGetCount()
        print("GPU个数：", gpu_device_count)
        gpu_info_list = []
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

            # print("第 %d 张卡：" % i, "-" * 30)
            # print("显卡名：", gpu_name)
            # print("内存总容量：", memory_info.total / self.unit, "MB")
            # print("使用容量：", memory_info.used / self.unit, "MB")
            # print("剩余容量：", memory_info.free / self.unit, "MB")
            # print("显存空闲率：", memory_info.free / memory_info.total)
            # print("温度：", gpu_temperature, "摄氏度")
            # # print("风扇速率：", gpu_fan_speed)
            # print("供电水平：", gpu_power_state)
            # print("gpu计算核心满速使用率：", gpu_util_rate)
            # print("gpu内存读写满速使用率：", gpu_memory_rate)
            # print("内存占用率：", memory_info.used / memory_info.total)

            info = {
                'gpuName': gpu_name,
                'memoryTotal': memory_info.total / self.unit,
                'memoryUsed': memory_info.used / self.unit,
                'memoryFree': memory_info.free / self.unit,
                'freeRate': memory_info.free / memory_info.total,
                'usedRate': memory_info.used / memory_info.total,
                'temperature': gpu_temperature,
                'powerSupplyLevel': gpu_power_state,
                'gpuUtilRate': gpu_util_rate,
                'gpuMemoryRate': gpu_memory_rate
            }

            gpu_info_list.append(info)

            """
            # 设置显卡工作模式
            # 设置完显卡驱动模式后，需要重启才能生效
            # 0 为 WDDM模式，1为TCC 模式
            gpuMode = 0     # WDDM
            gpuMode = 1     # TCC
            pynvml.nvmlDeviceSetDriverModel(handle, gpuMode)
            # 很多显卡不支持设置模式，会报错
            # pynvml.nvml.NVMLError_NotSupported: Not Supported
            """
            # 对pid的gpu消耗进行统计
            # 获取所有GPU上正在运行的进程信息
            # pid_all_info = pynvml.nvmlDeviceGetComputeRunningProcesses(handle)
            # for pid_info in pid_all_info:
            #     pid_user = psutil.Process(pid_info.pid).username()
            #     # 统计某pid使用的显存
            #     print("进程pid：", pid_info.pid, "用户名：", pid_user, "显存占有：", pid_info.usedGpuMemory / self.unit,
            #           "Mb")
        # 最后关闭管理工具
        pynvml.nvmlShutdown()
        return gpu_info_list
