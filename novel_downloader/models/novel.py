from dataclasses import dataclass, field
from typing import List, Dict, Any
from novel_downloader.models.config import SaveMethodConfig


@dataclass
class Chapter:
    """章节数据"""
    title: str
    root:str
    url: str|None = None
    order: int = 0
    volume:str = ""
    content: str = ""
    timestamp: float = 0
    count:int = 0
    is_complete: bool = False
    images: List[tuple[str]] = field(default_factory=list)

@dataclass
class Config:
    hash: str
    version: str = "1.1.0"
    url: str|None = None
    name: str = ""
    group: str = "Default"
    max_retry: int = 3
    timeout: int = 10
    interval: float = 2.0
    delay: list[float] = field(default_factory=lambda: [1.0, 3.0])
    save_method: SaveMethodConfig = field(default_factory=SaveMethodConfig)
    first_time: float = 0
    last_control_time: float = 0


@dataclass
class Novel:
    """小说数据"""
    url: str
    name: str
    author: str | None = None
    author_description: str | None = None
    tags: List[str] = field(default_factory=list)
    description: str | None = None
    count: int = 0
    last_update_chapter: str | None = None
    last_update_time: float | None = None
    rating: float | None = None
    cover_image_data: str | None = None
    chapters: List[Chapter] = field(default_factory=list)
    config: Config = field(default_factory=Config)

    # 索引字段
    _chapter_by_url: Dict[str, Chapter] = field(default_factory=dict, init=False)
    _chapter_by_order: Dict[int, Chapter] = field(default_factory=dict, init=False)

    def __add__(self,chapter):
        if chapter.url:
            self._chapter_by_url[chapter.url] = chapter
        if chapter.order!=0:
            self._chapter_by_order[chapter.order] = chapter
        self.chapters = list(self._chapter_by_order.values())
        return self

    def __getitem__(self, index):
        if isinstance(index,str):
            return self._chapter_by_url.get(index)
        if isinstance(index,int):
            return self._chapter_by_order.get(index)
        return None

    def find_chapter(self, key: str | int | Any) -> Chapter | None:
        """查找章节"""
        if isinstance(key, str) and key.startswith("https://"):
            return self._chapter_by_url.get(key)
        elif isinstance(key, int):
            return self._chapter_by_order.get(key)
        else:
            raise KeyError(f"不支持的查找键类型: {type(key)}")
