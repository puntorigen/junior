# utilities for system operations
import psutil
import shutil
import GPUtil
import cpuinfo
import speedtest

class SystemInfo:
    @staticmethod
    def get_memory_info():
        """Get the available and total memory in bytes."""
        mem = psutil.virtual_memory()
        return {
            "total": mem.total,
            "available": mem.available
        }

    @staticmethod
    def get_disk_info(path="/"):
        """Get the available and total disk space in bytes for the given path."""
        disk = shutil.disk_usage(path)
        return {
            "total": disk.total,
            "free": disk.free
        }

    @staticmethod
    def get_cpu_info():
        """Get the number of CPU cores and the CPU speed."""
        cpu_info = cpuinfo.get_cpu_info()
        return {
            "count": psutil.cpu_count(logical=True),
            "physical_cores": psutil.cpu_count(logical=False),
            "brand": cpu_info.get("brand_raw"),
            "hz_actual": cpu_info.get("hz_actual")[0],
            "hz_advertised": cpu_info.get("hz_advertised")[0],
            "l3_cache": cpu_info.get("l3_cache_size")
        }

    @staticmethod
    def get_gpu_info():
        """Get information about available GPUs."""
        gpus = GPUtil.getGPUs()
        gpu_info_list = []
        for gpu in gpus:
            gpu_info = {
                "id": gpu.id,
                "name": gpu.name,
                "total_memory": gpu.memoryTotal,
                "free_memory": gpu.memoryFree,
                "used_memory": gpu.memoryUsed,
                "gpu_util": gpu.load * 100,
                "temperature": gpu.temperature
            }
            gpu_info_list.append(gpu_info)
        return gpu_info_list

    @staticmethod
    def basic_benchmark():
        """Get basic benchmarking scores, such as CPU speed and internet speed."""
        cpu_info = SystemInfo.get_cpu_info()
        speed_test = speedtest.Speedtest()
        speed_test.get_best_server()
        speed_test.download()
        speed_test.upload()
        results = speed_test.results.dict()

        return {
            "cpu_speed_score": cpu_info["hz_actual"],
            "download_speed_mbps": results["download"] / 1e6,
            "upload_speed_mbps": results["upload"] / 1e6,
            "ping_ms": results["ping"]
        }

    @staticmethod
    def get_all_info():
        """Get all system information."""
        return {
            "memory": SystemInfo.get_memory_info(),
            "disk": SystemInfo.get_disk_info(),
            "cpu": SystemInfo.get_cpu_info(),
            "gpu": SystemInfo.get_gpu_info(),
            "benchmark": SystemInfo.basic_benchmark()
        }

# Example Usage
if __name__ == "__main__":
    system_info = SystemInfo.get_all_info()
    for key, value in system_info.items():
        print(f"{key.capitalize()}: {value}")
