import re
import time

from novel_downloader import UserSpecificConfig
from novel_downloader.models import DownloadMode
from novel_downloader.models.novel import *
from novel_downloader.parsers.base import BaseParser
from bs4 import BeautifulSoup
from colorama import Fore

from novel_downloader.core.downloader import ChromeDownloader, APIDownloader, RequestsDownloader

def user_state(html):
    soup = BeautifulSoup(html, 'lxml')
    # 右上角登录界面
    user_info_div = soup.find("div", class_="nri")
    if user_info_div is None:
        user_state_code = -1
    else:
        user_state_code = 1
    match user_state_code:
        case -1:
            print(f"{Fore.YELLOW}笔趣阁账号未登录")
        case 1:
            print(f"{Fore.GREEN}笔趣阁账号已登录")

class BiqugeForHtml(BaseParser):
    def __init__(self, config: UserSpecificConfig, downloader: ChromeDownloader | APIDownloader | RequestsDownloader):
        self.config = config
        self.downloader = downloader

    def parse_novel_info(self, url: str, threading_id, **kwargs) -> Novel:

        label = []
        last_update_for_chapter, last_update_for_time = None, None
        soup = BeautifulSoup(kwargs['html'], 'html.parser')
        info_data = soup.find("div", id="info")  # 信息
        name = info_data.find("h1").get_text()
        p_list = info_data.find_all("p")
        author = ""
        for p in p_list:
            if p.text.startswith("作  者："):
                author = p.find("a").get_text()
            if p.text.startswith("分  类："):
                label = [p.find("a").get_text()]
            if p.text.startswith("最后更新："):
                last_update_for_time = time.mktime(time.strptime(p.text[5:], "%Y-%m-%d %H:%M:%S"))
            if p.text.startswith("最新更新："):
                last_update_for_chapter = p.get_text()
        book_cover_url = soup.find("div", id="fmimg").find("img").get("src")
        book_cover_data = ''  # base64.b64encode(requests.get(book_cover_url).content).decode("utf-8") # 访问会卡在这里
        web_chapter_list = soup.find('div', id='list').find_all('dd')
        abstract = soup.find("div", id="intro").get_text()
        # 更新小说信息

        if self.config.get_mode == DownloadMode.BROWSER:
            config = self.config.browser
        else:
            config = self.config.requests["Fanqie"]

        # 更新小说信息
        novel_config = Config(version="1.2.0",
                              hash=str(abs(hash(name))),
                              url=url,
                              name=name,
                              group=self.config.group,
                              max_retry=config.max_retry,
                              timeout=config.timeout,
                              interval=config.interval,
                              delay=config.delay,
                              first_time=time.time(),
                              last_control_time=time.time()
                              )
        novel = Novel(
            url=url,
            name=name,
            author=author,
            tags=label,
            description=abstract,
            last_update_chapter=last_update_for_chapter,
            last_update_time=last_update_for_time,
            config=novel_config,
        )
        # 更新下载列表
        all_title_list = [title.find("a").get("title") for title in web_chapter_list]
        all_url_list = ["https://www.biqugequ.org/" + url.find("a").get("href") for url in web_chapter_list]
        order = 1
        for title, chapter_url in zip(all_title_list, all_url_list):
            chapter = Chapter(title=title,
                              root=url,
                              url=chapter_url,
                              order=order)
            novel+=chapter
        return novel

    def parse_chapter_content(self, url, threading_id, novel: Novel, **kwargs)->tuple[str,str|None]:
        # 笔趣阁，一章分页设计
        url_id = re.findall(r"(\d+).html", url)
        soup = BeautifulSoup(kwargs['html'], 'lxml')
        novel_content_div = soup.find('div', id='content').find_all("p")
        next_url = soup.find("div", class_="bottem2").find("a", id="pager_next").get("href")
        # 当下一页是当前章节的下一分页时
        if re.search(rf"{url_id}_\d.html", next_url):
            next_url = "https://www.biqugequ.org" + next_url
            novel_content_div = novel_content_div[:-1]
        else:
            next_url = None
        for p in novel_content_div:
            kwargs['content'] += p.get_text() + '\n'
        return kwargs['content'], next_url


class BiqugeForBrowser(BiqugeForHtml):
    def __init__(self, config: UserSpecificConfig, downloader: ChromeDownloader):
        super().__init__(config, downloader)

    def _browser_get_html(self, url: str, threading_id) -> str | None | Any:
        self.downloader.get(url=url, threading_id=threading_id)
        html = self.downloader.download(url=url, threading_id=threading_id)
        return html

    def parse_novel_info(self, url: str, threading_id, **kwargs):
        html = self._browser_get_html(url, threading_id=threading_id)
        user_state(html)
        return super().parse_novel_info(url, threading_id=threading_id, html=html)

    def parse_chapter_content(self, url, threading_id, novel, **kwargs) ->tuple[Novel,tuple[Chapter]]:
        if 'content' not in kwargs.keys():
            kwargs['content'] = ""
        html = self._browser_get_html(url, threading_id=threading_id)
        content,next_url=super().parse_chapter_content(url, threading_id=threading_id, html=html, novel=novel,content=kwargs['content'])
        if next_url is None:
            chapter = novel[url]
            chapter.content = content
            chapter.is_complete = True
            novel+=chapter
            return novel,(chapter,)
        else:return self.parse_chapter_content(next_url, threading_id, novel, content=content)


class BiqugeForReq(BiqugeForHtml):
    def __init__(self, config: UserSpecificConfig, downloader: ChromeDownloader | APIDownloader | RequestsDownloader):
        super().__init__(config, downloader)

    def __str__(self):
        return "暂未开发完成"


class BiqugeParser(BaseParser):
    def __init__(self, config: UserSpecificConfig, downloader: ChromeDownloader | APIDownloader | RequestsDownloader):
        self.config = config
        self.downloader = downloader
        if self.config.get_mode == DownloadMode.BROWSER:
            self._parser = BiqugeForBrowser(self.config, self.downloader)
        elif self.config.get_mode == DownloadMode.API:
            raise ValueError("笔趣阁解析器暂不支持API")
        elif self.config.get_mode == DownloadMode.REQUESTS:
            self._parser = BiqugeForReq(self.config, self.downloader)

    def parse_novel_info(self, url: str, threading_id, **kwargs) -> Novel:
        return self._parser.parse_novel_info(url, threading_id=threading_id)

    def parse_chapter_content(self, url, threading_id, novel: Novel, **kwargs) -> tuple[Novel, tuple[Chapter, ...]]:
        self._parser:BiqugeForBrowser = BiqugeForBrowser(self.config, self.downloader)
        return self._parser.parse_chapter_content(url=url, threading_id=threading_id, novel=novel,content="")
