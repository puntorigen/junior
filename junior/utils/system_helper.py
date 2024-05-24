import platform
import psutil
import shutil
import cpuinfo
import speedtest

class SystemInfo:
    @staticmethod
    def get_memory_info():
        """Get the available and total memory in GB."""
        mem = psutil.virtual_memory()
        return {
            "total": mem.total/1024/1024/1024,
            "available": mem.available/1024/1024/1024
        }

    @staticmethod
    def get_disk_info(path="/"):
        """Get the available and total disk space in GB for the given path."""
        disk = shutil.disk_usage(path)
        return {
            "total": disk.total/1024/1024/1024,
            "free": disk.free/1024/1024/1024
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
    def is_silicon_mac() -> bool:
        """Check if the system is a silicon-based Mac (e.g., M1, M2)."""
        return platform.system() == "Darwin" and platform.machine() == "arm64"

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
    def get_basic_info():
        """Get basic system memory information."""
        return {
            "memory": SystemInfo.get_memory_info(),
            "disk": SystemInfo.get_disk_info()
        }
    
    @staticmethod
    def get_all_info():
        """Get all system information."""
        return {
            "memory": SystemInfo.get_memory_info(),
            "disk": SystemInfo.get_disk_info(),
            "cpu": SystemInfo.get_cpu_info(),
            "benchmark": SystemInfo.basic_benchmark(),
            "is_silicon_mac": SystemInfo.is_silicon_mac()
        }

# Example Usage
if __name__ == "__main__":
    system_info = SystemInfo.get_all_info()
    for key, value in system_info.items():
        print(f"{key.capitalize()}: {value}")

    # Check if the system is a silicon-based Mac
    if SystemInfo.is_silicon_mac():
        print("This is a silicon-based Mac (e.g., M1, M2).")
    else:
        print("This is not a silicon-based Mac.")
