import os
import platform
import subprocess
import time

from tqdm import tqdm

from novel_downloader import NovelDownloader, DownloaderFactory
from novel_downloader.core import check
from novel_downloader.core.config import ConfigManagerForUnion


class ND(NovelDownloader):
    def __init__(self):
        self.config_manager = ConfigManagerForUnion()
        self.config = self.config_manager.config
        super().__init__(self.config_manager.config)
    def get_info(self, download_url):
        novel_ = super().get_info(url=download_url)
        return novel_
if __name__ == "__main__":
    check()
    nd=ND()
    while True:
        select = input(
            "\n"
            "请输入功能:\n"
            "0.网站登录：\n"
            "2.下载：\n"
            "3.批量下载：\n"
        ).strip()
        match select:
            case "0":
                option = input("""请选择网站：
                1.番茄：
                2.起点：
                3.笔趣阁(www.biqugequ.org)：
                """)

                print("登录后按下任意键继续..")
                time.sleep(0.5)
                if option == '1':
                    downloader = DownloaderFactory.create_downloader(nd.config, website="fanqie")
                    downloader.get("https://fanqienovel.com/main/writer/login", threading_id=0)
                elif option == "2":
                    downloader = DownloaderFactory.create_downloader(nd.config, website="fanqie")
                    downloader.get("https://www.qidian.com", threading_id=0)
                elif option == '3':
                    downloader = DownloaderFactory.create_downloader(nd.config, website="biquge")
                    downloader.get("https://biqugequ.org", threading_id=0)
                else:
                    print("请指定网站")
                    continue
                input()

            case "2":
                url = input("请输入小说链接：")
                novel = nd.get_info(download_url=url)
                if not novel.chapters:
                    down_progress = tqdm(desc=novel.name)
                    while True:
                        novel, chapters = nd.get_chapter(url=None, threading_id=0, novel=novel)
                        if chapters[0] is not None:
                            nd.save_novel(nd.config.save_method, chapters=chapters, novel=novel)
                            down_progress.update(1)
                        else:
                            down_progress.close()
                            break
                else:
                    down_progress = tqdm(total=len(novel.chapters), desc=novel.name)
                    index = 1
                    while True:
                        if index <= len(novel.chapters):
                            chapter_url = novel[index].url
                            novel, chapters = nd.get_chapter(url=chapter_url, threading_id=0, novel=novel)
                            nd.save_novel(nd.config.save_method, chapters=chapters, novel=novel)
                            down_progress.update(1)
                            index += 1
                        else:
                            down_progress.close()
                            break

            case "3":
                filename = os.path.join("data", "Local", "urls.txt")
                if not os.path.exists(filename):
                    open(filename, encoding="utf-8").close()
                print(
                    """将打开urls.txt,请在文件中输入小说链接，一行一个。输入完成后请保存并关闭文件，然后按 Enter 键继续...""")
                time.sleep(0.5)
                system = platform.system()
                if system == "Windows":
                    os.startfile(filename)
                elif system == "Darwin":  # macOS
                    subprocess.run(['open', filename])
                else:  # Linux 和其他Unix系统
                    try:
                        subprocess.run(['xdg-open', filename])
                    except FileNotFoundError:
                        print("无法打开文件，请检查系统")
                input()
                with open(filename, encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("#"): continue
                        novel = nd.get_info(download_url=line)
                        if not novel.chapters:
                            down_progress = tqdm(desc=novel.name)
                            while True:
                                novel, chapters = nd.get_chapter(url=None, threading_id=0, novel=novel)
                                if chapters[0] is not None:
                                    nd.save_novel(nd.config.save_method, chapters=chapters, novel=novel)
                                    down_progress.update(1)
                                else:
                                    down_progress.close()
                                    break
                        else:
                            down_progress = tqdm(total=len(novel.chapters), desc=novel.name)
                            index = 1
                            while True:
                                if index <= len(novel.chapters):
                                    chapter_url = novel[index].url
                                    novel, chapters = nd.get_chapter(url=chapter_url, threading_id=0, novel=novel)
                                    nd.save_novel(nd.config.save_method, chapters=chapters, novel=novel)
                                    down_progress.update(1)
                                    index += 1
                                else:
                                    down_progress.close()
                                    break
