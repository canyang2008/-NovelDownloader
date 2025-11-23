from enum import Enum


class DownloadMode(Enum):
    """下载模式枚举"""
    BROWSER = 0
    API = 1
    REQUESTS = 2