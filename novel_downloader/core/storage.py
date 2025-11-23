import json
import os
import shutil
from datetime import datetime
from typing import Dict, Any, List
import hashlib


class NovelStorage:
    """小说存储管理"""

    def __init__(self, config):
        self.config = config
        self._ensure_dirs()
        self._last_backup_time = {}

    def _ensure_dirs(self):
        """确保目录存在"""
        pass

    def save_novel_config(self, novel_id: str, data: Dict[str, Any],
                          operation: str = "auto") -> bool:
        """保存小说配置"""
        pass

    def _should_backup(self, novel_id: str, new_data: Dict[str, Any],
                       operation: str) -> bool:
        """智能判断是否需要备份"""
        pass

    def _detect_significant_changes(self, old_data: Dict[str, Any],
                                    new_data: Dict[str, Any]) -> bool:
        """检测是否有重大变化"""
        pass

    def _recent_chapters_changed(self, old_data: Dict[str, Any],
                                 new_data: Dict[str, Any]) -> bool:
        """检查最近章节是否有变化"""
        pass

    def load_novel_config(self, novel_id: str):
        """加载小说配置"""
        pass

    def _get_config_path(self, novel_id: str) -> str:
        """获取配置文件路径"""
        pass

    def _save_images(self, novel_id: str, images: Dict[str, Any]):
        """保存图片数据到单独文件"""
        pass

    def _load_images(self, novel_id: str) -> Dict[str, Any]:
        """加载图片数据"""
        pass

    def _backup_config(self, novel_id: str) -> str:
        """备份配置"""
        pass

    def _cleanup_old_backups(self, backup_dir: str):
        """清理旧备份"""
        pass