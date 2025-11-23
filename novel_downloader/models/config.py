from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional

from novel_downloader.models import DownloadMode
from novel_downloader.models.backup import BackupConfig
from novel_downloader.models.group import GlobalGroupConfig
from novel_downloader.models.save import SaveMethodConfig


@dataclass
class BrowserConfig:
    """浏览器通用配置"""
    timeout: int = 10
    max_retry: int = 3
    interval: float = 2.0
    delay: List[float] = field(default_factory=lambda: [1.0, 1.5])
    port: int = 9445
    headless: bool = False
    user_data_dir: str = ""  # 将从GlobalUserConfig获取

    # 网站特定的浏览器状态
    site_states: Dict[str, int] = field(default_factory=dict)


@dataclass
class ApiProviderConfig:
    """API提供商配置"""
    name: str = ""  # API名称
    max_retry: int = 3
    timeout: int = 10
    interval: float = 2.0
    delay: List[float] = field(default_factory=lambda: [1.0, 3.0])
    key: str = ""
    endpoint: str = ""
    headers: Dict[str, str] = field(default_factory=dict)
    params: Dict[str, Any] = field(default_factory=dict)
    # 其他提供商特定字段
    extra_params: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True  # 是否启用


@dataclass
class SiteApiConfig:
    """网站API配置"""
    option: str = ""  # 当前选择的API
    providers: Dict[str, ApiProviderConfig] = field(default_factory=dict)

    def get_active_provider(self) -> Optional[ApiProviderConfig]:
        """获取当前激活的API提供商"""
        if self.option and self.option in self.providers:
            return self.providers[self.option]
        return None


@dataclass
class SiteRequestsConfig:
    """网站Requests配置"""
    max_retry: int = 3
    timeout: int = 10
    interval: float = 2.0
    delay: List[float] = field(default_factory=lambda: [1.0, 3.0])
    cookie: str = ""
    headers: Dict[str, str] = field(default_factory=dict)
    proxies: Dict[str, str] = field(default_factory=dict)


@dataclass
class UserSpecificConfig:
    """用户特定配置"""
    version: str = "1.1.0"
    user_name: str = "Default"
    group: str = "Default"
    readme: str = ""
    play_completion_sound: bool = False
    get_mode: DownloadMode = DownloadMode.BROWSER  # 0=Browser, 1=API, 2=Requests

    # 线程配置
    threading_number: int = 3

    # 下载配置
    browser: BrowserConfig = field(default_factory=BrowserConfig)
    api: Dict[str, SiteApiConfig] = field(default_factory=dict)  # 网站 -> API配置
    requests: Dict[str, SiteRequestsConfig] = field(default_factory=dict)

    # 组配置
    groups: GlobalGroupConfig = field(default_factory=GlobalGroupConfig)

    # 保存配置
    save_method: SaveMethodConfig = field(default_factory=SaveMethodConfig)

    # 备份配置
    backup: BackupConfig = field(default_factory=BackupConfig)

    # 未处理项目（用于扩展）
    unprocess: List[Any] = field(default_factory=list)
