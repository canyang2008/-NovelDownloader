from dataclasses import dataclass, field
from typing import List,Any

@dataclass
class GroupConfig:
    """分组配置"""
    group_name:str = "Default"
    members: List[Any|None] = field(default_factory=list)

@dataclass
class GlobalGroupConfig:
    """全局分组配置"""
    version: str = "1.1.0"
    readme: str = ""
    current_group: str = "Default"
    groups: dict[str,GroupConfig] = field(default_factory=dict)

