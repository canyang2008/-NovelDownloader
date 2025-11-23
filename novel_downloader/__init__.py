from . import parsers
from .models.config import UserSpecificConfig
from .models.save import SaveMethodConfig
from .outputs.root import ROOTOutput
from .outputs.txt import TXTOutput
from .parsers import url_parse
from .parsers.fanqie import FanqieForHtml, FanqieForBrowser
from .core.config import ConfigManagerForUnion
from .core.downloader import DownloaderFactory
from .core.storage import NovelStorage
from .models.novel import Novel, Chapter
from .models.novel import Config as NovelConfig
from typing import Dict, Any
import importlib
import os
import threading
import novel_downloader.parsers.base


class NovelDownloader:
    """小说下载器主类"""

    def __init__(self, config: UserSpecificConfig = None):

        self.downloader = None
        self.config = config
        # 加载解析器
        self.parser = None
        self.parsers = self._load_parsers()
        self.origin_outputs = self._load_outputs()
        self.outputs = {}

        # 多线程
        self._download_lock = threading.Lock()

        self.origin_url = ""
        self.download_url = ""

        self.website = ""

        self._user = "Default"
        self._group = "Default"
        self._novel_name = ""
    @staticmethod
    def _load_parsers() -> Dict[str, Any]:
        """动态加载解析器"""
        parsers = {}
        parsers_dir = os.path.join(os.path.dirname(__file__), 'parsers')
        for file in os.listdir(parsers_dir):
            if file.endswith('.py') and file not in ['__init__.py', 'base.py']:
                module_name = file[:-3]
                try:
                    module = importlib.import_module(f'novel_downloader.parsers.{module_name}', __name__)
                    parser_class = getattr(module, f'{module_name.capitalize()}Parser')
                    parsers[module_name] = parser_class
                except (ImportError, AttributeError) as e:
                    print(f"加载解析器 {module_name} 失败: {e}")

        return parsers
    @staticmethod
    def _load_outputs() -> Dict[str, Any]:
        """动态加载输出格式"""
        outputs = {}
        outputs_dir = os.path.join(os.path.dirname(__file__), 'outputs')

        for file in os.listdir(outputs_dir):
            if file.endswith('.py') and file not in ['__init__.py', 'base.py']:
                module_name = file[:-3]
                try:
                    module = importlib.import_module(f'.outputs.{module_name}', __name__)
                    output_class = getattr(module, f'{module_name.upper()}Output')
                    outputs[module_name] = output_class
                except (ImportError, AttributeError) as e:
                    print(f"加载输出格式 {module_name} 失败: {e}")

        return outputs

    def _load_novel_config(self):pass

    def get_info(self, url) -> Novel:
        """获取小说信息"""
        url,website = url_parse(url)
        self.downloader = DownloaderFactory.create_downloader(self.config, website)
        self.parser:FanqieForBrowser = self.parsers.get(website, None)(config = self.config, downloader = self.downloader)
        self.website = website
        novel = self.parser.parse_novel_info(url=url, threading_id=0)
        self._novel_name = novel.name
        return novel

    def get_chapter(self, url, threading_id: int, novel) -> tuple[Novel, tuple[Chapter]]:
        """下载单个章节"""
        return self.parser.parse_chapter_content(url, threading_id, novel)

    def update_novel(self, url,novel,) -> bool:
        """更新小说"""
        pass

    def save_novel(self, save_method:SaveMethodConfig, chapters: tuple[Chapter], novel: Novel) -> bool:
        """保存小说"""
        if not self.outputs.get("root"):
            self.outputs['root'] = self.origin_outputs["root"](self._user, self._group, self._novel_name)
        self.outputs['root'].save(save_method=save_method.root, chapters=chapters, novel=novel)
        if save_method.json.enable:
            if not self.outputs.get('json'):
                self.outputs['json'] = self.origin_outputs['json'](self._user, self._group, self._novel_name)
            self.outputs['json'].save(save_method.json, chapters, novel)
        if save_method.txt.enable:
            if not self.outputs.get('txt'):
                self.outputs['txt'] = self.origin_outputs["txt"](self._user, self._group, self._novel_name)
            self.outputs["txt"].save(save_method.txt, chapters, novel)
        return True

    def add_user(self, user_id: str, user_data: Dict[str, Any]):
        """添加用户"""
        pass

    def reset(self):
        """重设参数"""
        pass

    def create_group(self, group_name: str, group_data: Dict[str, Any]):
        """创建分组"""
        pass

    def backup(self, novel_id: str) -> str:
        """手动触发备份"""
        pass

    def backup_all_novels(self) -> Dict[str, str]:
        """备份所有小说"""
        pass