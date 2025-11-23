import os
import re
import time

from novel_downloader.outputs import dir_transform
from .base import BaseOutput
from ..models.save import TxtSaveConfig


class TXTOutput(BaseOutput):
    """TXT输出格式"""
    def __init__(self,user,group,novel_name):
        self.file_path = None
        self.user = user
        self.group = group
        self.novel_name = novel_name
        self.file = None
    def save(self, save_method:TxtSaveConfig,chapters,novel):
        """保存为TXT格式"""
        if self.file is None:
            file_dir = dir_transform(path=save_method.dir, user=self.user, group=self.group, name=self.novel_name)
            self.file_path = os.path.join(file_dir, self.novel_name+".txt")
            open(self.file_path, 'w', encoding="utf-8").close()
            os.makedirs(file_dir,exist_ok=True)
            self.file = open(self.file_path, "a", encoding='utf-8')

            info_text = (  # 生成小说信息文本
                f"小说名：{self.novel_name}\n作者：{novel.author}\n"
                f"简介：{novel.description}\n标签：{' '.join(novel.tags)}\n"
                f"""字数：{novel.count}\n最后更新：{novel.last_update_chapter} {time.strftime('%Y-%m-%d %H:%M:%S',
                                                                                            time.localtime(novel.last_update_time))}\n"""
                f"链接：{novel.url}\n\n"
            )
            self.file.write(info_text)

        for chapter in chapters:
            if chapter:
                content = '\t'+chapter.content.replace("\n","\n\t")
                content = re.sub(r'<&!img\?group_id=\d+/!&>', '', content)   # 去掉图片占位字符串
                chapter_text = (                                       # 格式化文本
                f"{chapter.title}\n    "
                f"更新字数：{chapter.count}    "
                f"更新时间：{time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(chapter.timestamp))}\n\n"
                f"{content}\n\n"
                )
                self.file.write(chapter_text)