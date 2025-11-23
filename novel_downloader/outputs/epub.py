from typing import Dict, Any

from .base import BaseOutput
from ebooklib import epub


class EPUBOutput(BaseOutput):
    """EPUB输出格式"""

    def save(self, save_method,chapters,novel):
        """保存为EPUB格式"""
        pass
    def update(self, novel: Dict[str, Any], save_method: str):
        pass