from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseOutput(ABC):
    """输出格式基类"""

    @abstractmethod
    def save(self, save_method,chapters,novel):
        """保存小说到指定格式"""
        pass
