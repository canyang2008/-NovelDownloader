from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseParser(ABC):
    """解析器基类"""

    @abstractmethod
    def parse_novel_info(self, url: str, threading_id, **kwargs) -> Dict[str, Any]:
        """解析小说信息"""
        pass

    @abstractmethod
    def parse_chapter_content(self, url, threading_id, novel, **kwargs) -> str:
        """解析章节内容"""
        pass
