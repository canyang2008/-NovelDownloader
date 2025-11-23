from dataclasses import dataclass, field


@dataclass
class SaveFormatConfig:
    """保存格式配置基类"""
    enable: bool = True
    name: str = "name_default"
    dir: str = "data\\Bookstore\\<User>\\<Group>\\<Name>"


@dataclass
class RootSaveConfig:
    """小说根数据保存独立配置"""
    dir: str = "data\\Local\\<User>\\json"

@dataclass
class JsonSaveConfig(SaveFormatConfig):
    """JSON保存配置"""
    img_dir: str = "data\\Bookstore\\<User>\\<Group>\\<Name>\\Img"
    pretty_print: bool = True
    ensure_ascii: bool = False


@dataclass
class TxtSaveConfig(SaveFormatConfig):
    """TXT保存配置"""
    gap: int = 0
    max_filesize: int = -1
    encoding: str = "utf-8"


@dataclass
class HtmlSaveConfig(SaveFormatConfig):
    """HTML保存配置"""
    one_file: bool = True
    template: str = "default"


@dataclass
class EpubSaveConfig(SaveFormatConfig):
    """EPUB保存配置"""
    css_style: str = "default"
    include_toc: bool = True


@dataclass
class SaveMethodConfig:
    """保存方法配置"""
    json: JsonSaveConfig = field(default_factory=JsonSaveConfig)
    txt: TxtSaveConfig = field(default_factory=TxtSaveConfig)
    html: HtmlSaveConfig = field(default_factory=HtmlSaveConfig)
    epub: EpubSaveConfig = field(default_factory=EpubSaveConfig)
    root: RootSaveConfig = field(default_factory=RootSaveConfig)

