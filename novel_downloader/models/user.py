from dataclasses import dataclass, field
from typing import Dict


@dataclass
class UserConfig:
    """用户配置"""
    user_config_path: str  # 用户配置文件路径
    user_data_dir: str     # 浏览器用户数据目录
    base_dir: str          # 保存基本小说信息的根目录

@dataclass
class GlobalUserConfig:
    """全局用户配置"""
    version: str = "1.1.0"
    readme: str = ""
    current_user: str = "Default"
    users: Dict[str, UserConfig] = field(default_factory=dict)

