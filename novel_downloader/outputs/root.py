import os
from typing import Dict, Any
import base64
from .base import BaseOutput
from ..models.save import RootSaveConfig
from . import dir_transform

class ROOTOutput(BaseOutput):
    """根数据输出"""

    def __init__(self,user,_,__):
        self.base_dir = None
        self.file_path = None
        self.img_dir = None
        self.user = user
        self.chapter_image_saved_index = []
    def _img_save(self, novel):
        if 0 not in self.chapter_image_saved_index:
            with open(os.path.join(self.img_dir,"0"),"w") as f:
                f.write(base64.b64encode(novel.cover_image_data).decode())
            self.chapter_image_saved_index.append(0)
        for chapter in novel.chapters:
            if chapter.order not in self.chapter_image_saved_index and chapter.images:
                for item in chapter.images:
                    with open(os.path.join(self.img_dir,f"({chapter.order}){item[0]}"),"w",encoding="utf-8") as f:
                        f.write(base64.b64encode(item[1]).decode())
                    self.chapter_image_saved_index.append(chapter.order)
    def save(self, save_method:RootSaveConfig, chapters, novel):
        if self.file_path is None:
            self.base_dir = dir_transform(path=save_method.dir, user=self.user, group=None, name=None)
            self.img_dir = os.path.join("data","Local","self.user","img",novel.name)
            os.makedirs(self.img_dir,exist_ok=True)
            self._img_save(novel=novel)
    def update(self, novel: Dict[str, Any], save_method: str):
        pass