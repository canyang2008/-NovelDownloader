import os
from typing import Dict, Any
import base64
from .base import BaseOutput
from ..models.save import RootSaveConfig, JsonSaveConfig
from . import dir_transform

class JSONOutput(BaseOutput):
    """JSON输出 - 当前仅输出图片"""

    def __init__(self, user, group, novel_name):
        self.file = None
        self.file_path = None
        self.img_dir = None
        self.user = user
        self.group = group
        self.novel_name = novel_name
        self.chapter_image_saved_index = []

    def _img_save(self, novel):
        if 0 not in self.chapter_image_saved_index:
            os.makedirs(os.path.join(self.img_dir, "封面图片"),exist_ok=True)
            with open(os.path.join(self.img_dir, "封面图片",f"{self.novel_name}.png"), "wb") as f:
                f.write(novel.cover_image_data)
            self.chapter_image_saved_index.append(0)
        for chapter in novel.chapters:
            if chapter.order not in self.chapter_image_saved_index and chapter.images:
                os.makedirs(os.path.join(self.img_dir,chapter.title),exist_ok=True)
                for item in chapter.images:
                    with open(os.path.join(self.img_dir,chapter.title,item[0]), "wb") as f:
                        f.write(item[1])
                    self.chapter_image_saved_index.append(chapter.order)
    def save(self, save_method:JsonSaveConfig, chapters, novel):
        if self.file is None:
            file_dir = dir_transform(path=save_method.dir, user=self.user, group=self.group, name=self.novel_name)
            self.file_path = os.path.join(file_dir,self.novel_name+".json")
            self.img_dir = dir_transform(path=save_method.img_dir, user=self.user, group=self.group, name=self.novel_name)
            os.makedirs(file_dir, exist_ok=True)
            self.file = open(self.file_path, "a+", encoding='utf-8')
        self._img_save(novel)