import re
import time

import requests

from novel_downloader import UserSpecificConfig
from novel_downloader.models import DownloadMode
from novel_downloader.models.novel import *
from novel_downloader.parsers.base import BaseParser
from bs4 import BeautifulSoup, Tag

from novel_downloader.core.downloader import ChromeDownloader, APIDownloader, RequestsDownloader


def user_state(html):
    soup = BeautifulSoup(html, 'lxml')
    user_info_div = soup.find("div", class_="ml-auto text-s-gray-900 text-bo2 relative group")
    if user_info_div:
        if user_info_div.find('Button'):
            user_state_code = -1
        else:user_state_code = 1
    else:user_state_code = -1
    return user_state_code

class QidianForHtml(BaseParser):
    def __init__(self, config: UserSpecificConfig, downloader: ChromeDownloader | APIDownloader | RequestsDownloader):
        self.config = config
        self.downloader = downloader

    def parse_novel_info(self, url: str, threading_id, **kwargs) -> Novel:

        soup = BeautifulSoup(kwargs['html'], 'lxml')
        # 获取网页内容
        name = soup.find('h1', id='bookName').get_text()
        if soup.find('div', class_='author-information'):  # 判断是否为起点特殊页面，以作者图片是否显示为准
            author = soup.find('a', class_='writer-name').get_text()
            author_desc = soup.find('div', class_='outer-intro').find('p').get_text()
            attribute_str = soup.find('p', class_='book-attribute').text
            attribute = attribute_str.split('·')
            label = [i.get_text() for i in soup.find('p', class_='all-label').find_all('a')]
            attribute.extend(label)  # 标签
            all_label = attribute
            intro = soup.find('p', class_='intro').get_text()
        else:
            intro = None
            author_desc = None
            all_label = []
            author = soup.find('span', class_='author').get_text()
        count_word_str = soup.find('p', class_='count').find('em').get_text()
        if count_word_str.endswith("万"):
            count_word = int(float(count_word_str[:-1])*10000)
        else:
            count_word = int(count_word_str)
        last_update_chapter = soup.find('a', class_='book-latest-chapter').get_text()[5:]
        last_update_time_str = soup.find('span',class_="update-time").get_text()
        last_update_time = time.mktime(time.strptime(last_update_time_str[5:], "%Y-%m-%d %H:%M:%S"))
        intro_detail = soup.find('p', id='book-intro-detail').get_text()  # 简介
        abstract = f'{intro}\n{intro_detail}'
        book_cover_url = 'https:' + soup.find('a', id='bookImg').find('img').get('src')  # 封面图片链接
        book_cover_data = requests.get(book_cover_url).content
        # 更新小说信息
        if self.config.get_mode == DownloadMode.BROWSER:
            config = self.config.browser
        else:
            config = self.config.requests["Qidian"]

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

        novel = Novel(url=url,
                      author=author,
                      name=name,
                      author_description=author_desc,
                      tags=all_label,
                      description=abstract,
                      count=count_word,
                      last_update_chapter=last_update_chapter,
                      last_update_time=last_update_time,
                      cover_image_data=book_cover_data, config=novel_config)

        # 获取章节列表
        chapters_items = soup.find('div', class_='catalog-all')
        order = 1
        for chapters_item in chapters_items:
            if type(chapters_item) is Tag:
                volume = chapters_item.find('h3', class_='volume-name').get_text().split("·")[0]
                title_list = [item.text for item in chapters_item.find_all("a",class_="chapter-name")]
                url_list = ["https:"+item.get("href") for item in chapters_item.find_all("a",class_="chapter-name")]
                for title, chapter_url in zip(title_list, url_list):
                    chapter = Chapter(title=title,
                                      root=url,
                                      url=chapter_url,
                                      order=order,
                                      volume=volume)
                    novel+=chapter
                    order += 1
        return novel

    def parse_chapter_content(self, url, threading_id, novel: Novel, **kwargs) -> tuple[Novel, tuple[Chapter]]:
        soup = BeautifulSoup(kwargs['html'], 'lxml')
        count_word_str = soup.find("div", class_="relative").find_all('span',
                                                                  class_='group inline-flex items-center mr-16px')[
            -1].get_text().split()[-1]
        count_word = int(re.findall(r'\d+', count_word_str)[0])
        update_time_str = soup.find('span', class_='chapter-date').get_text()
        update_time = time.mktime(time.strptime(update_time_str, "%Y年%m月%d日 %H:%M"))
        novel_content_soup = soup.find('main')
        if soup.find('div', class_='mt-16px'):
            integrity = False
            novel_content = '\n'.join([i.get_text().strip() for i in novel_content_soup])
        else:
            integrity = True
            novel_content = '\n'.join([i.get_text().strip() for i in novel_content_soup.find_all("span",class_ = "content-text")])
        # 更新小说信息
        chapter = novel[url]
        chapter.timestamp = update_time
        chapter.count = count_word
        chapter.content = novel_content
        chapter.is_complete = integrity
        novel+=chapter
        return novel, (chapter,)

class QidianForBrowser(QidianForHtml):
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

    def parse_chapter_content(self, url, threading_id, novel, **kwargs):
        html = self._browser_get_html(url, threading_id=threading_id)
        return super().parse_chapter_content(url, threading_id=threading_id, html=html, novel=novel)

class QidianForReq(QidianForHtml):
    def __init__(self, config: UserSpecificConfig, downloader: ChromeDownloader | APIDownloader | RequestsDownloader):
        super().__init__(config, downloader)

    def __str__(self):
        return "暂未开发完成"

class QidianParser(BaseParser):
    def __init__(self, config: UserSpecificConfig, downloader: ChromeDownloader | APIDownloader | RequestsDownloader):
        self.config = config
        self.downloader = downloader
        if self.config.get_mode == DownloadMode.BROWSER:
            self._parser = QidianForBrowser(self.config, self.downloader)
        elif self.config.get_mode == DownloadMode.API:
            raise ValueError("起点解析器暂不支持API")
        elif self.config.get_mode == DownloadMode.REQUESTS:
            self._parser = QidianForReq(self.config, self.downloader)

    def parse_novel_info(self, url: str, threading_id, **kwargs) -> Novel:
        return self._parser.parse_novel_info(url=url, threading_id=threading_id)

    def parse_chapter_content(self, url, threading_id, novel: Novel, **kwargs) -> tuple[Novel, tuple[Chapter, ...]]:
        return self._parser.parse_chapter_content(url=url, threading_id=threading_id, novel=novel)
