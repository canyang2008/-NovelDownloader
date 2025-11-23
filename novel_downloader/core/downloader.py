import copy
import random
import threading
import time
from dataclasses import field

from DrissionPage import Chromium,ChromiumOptions
from DrissionPage.common import Settings
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from novel_downloader import UserSpecificConfig
from novel_downloader.models import DownloadMode


class ThreadingTimeout:
    def __init__(self, seconds):
        self.seconds = seconds
        self.timer = None
        self.timed_out = False

    def __enter__(self):
        self.timed_out = False
        self.timer = threading.Timer(self.seconds, self._timeout)
        self.timer.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.timer:
            self.timer.cancel()
        if self.timed_out:
            raise TimeoutError(f"Operation timed out after {self.seconds} seconds")
        return False

    def _timeout(self):
        self.timed_out = True

class DownloaderFactory:
    """下载器工厂"""

    @staticmethod
    def create_downloader(config: UserSpecificConfig, website=None):
        """创建下载器"""
        if config.get_mode == DownloadMode.REQUESTS:
            return RequestsDownloader(config, website)
        elif config.get_mode == DownloadMode.BROWSER:
            return ChromeDownloader(config)
        elif config.get_mode == DownloadMode.API:
            return APIDownloader(config, website)
        else:
            raise ValueError(f"不支持的下载模式: {config.get_mode.value}")


class BaseDownloader:
    """下载器基类"""

    def __init__(self, config: UserSpecificConfig):
        self.config = config
        self.threading_number = config.threading_number


    def get(self, url, threading_id: int):
        """访问网站"""
        pass

    def download(self, url: str, threading_id) -> str:
        """下载内容"""
        pass


class ChromeDownloader(BaseDownloader):
    """Chrome下载器"""

    def __init__(self, config: UserSpecificConfig):
        super().__init__(config)
        chrome_config = config.browser
        self.delay = chrome_config.delay
        self.headless = chrome_config.headless
        self.interval = chrome_config.interval
        self.timeout = chrome_config.timeout
        self.max_retry = chrome_config.max_retry
        self.user_data_dir = chrome_config.user_data_dir
        self.port = chrome_config.port
        self.driver = self._init_driver()
        self.tabs = []
        self.set_new_tab()

    def _init_driver(self):
        """初始化浏览器驱动"""
        co = ChromiumOptions()
        co = co.set_user_data_path(self.user_data_dir)
        co = co.set_local_port(self.port)
        co = co.headless(self.headless)
        return Chromium(addr_or_opts=co)

    def set_new_tab(self, set_number:int=None):
        if set_number is None:
            set_number = self.threading_number
        Settings.set_singleton_tab_obj(False)
        for index in range(set_number):
            self.tabs.append(self.driver.new_tab())

    def get(self, url, threading_id: int, retry: int = 0):
        """访问网站"""
        try:
            self.tabs[threading_id].get(url, retry=self.max_retry, interval=self.interval, timeout=self.timeout)
            time.sleep(random.uniform(*self.delay))
        except TimeoutError:
            raise TimeoutError(f"Operation timed out after {self.max_retry} seconds")

    def download(self, url: str, threading_id, retry:int = 0) -> str:
        """下载内容"""
        try:
            with ThreadingTimeout(self.timeout):
                response:str = self.tabs[threading_id].raw_data
        except TimeoutError:
            if retry <= self.max_retry:
                return self.download(url, threading_id, retry=retry + 1)
            else:
                raise TimeoutError(f"Operation timed out after {self.max_retry} seconds")
        return response



class APIDownloader(BaseDownloader):
    """API下载器"""
    def __init__(self, config: UserSpecificConfig,website:str = None):
        super().__init__(config)
        self.sessions:list[requests.Session] = []
        self.responses:list[requests.Response|None] = []
        self.website = website.capitalize()
        website_api_config = self.config.api[self.website]
        self.api_config = website_api_config.providers[website_api_config.option]
        self.max_retry = self.api_config.max_retry
        self.interval = self.api_config.interval
        self.delay = self.api_config.delay
        self.timeout = self.api_config.timeout
        self.key = self.api_config.key
        self._set_new_session()
        if not self.api_config.headers:
            self.headers:dict[str, str] = field(default_factory=lambda:{
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive'
            })

    def _set_new_session(self):
        retry_strategy = Retry(
            total=3,
            backoff_factor=self.interval - 1,
            status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        template_session = requests.Session()
        template_session.mount("https://", adapter)
        for index in range(self.threading_number):
            self.responses.append(None)
            session = copy.deepcopy(template_session)
            self.sessions.append(session)

    def get(self, url, threading_id: int, retry: int = 0, post_data: dict = None):
        """访问网站"""
        try:
            with ThreadingTimeout(self.timeout):
                response = self.sessions[threading_id].post(url,data=post_data, timeout=self.timeout)
            self.responses[threading_id] = response
            time.sleep(random.uniform(*self.delay))
        except TimeoutError:
            if retry <= self.max_retry:
                self.get(url, threading_id, retry + 1)

    def download(self, url: str, threading_id, retry = 0) -> dict:
        """下载内容"""

        response = self.responses[threading_id]
        response.encoding = 'utf-8'
        if not self.sessions[threading_id].cookies:
            cookie = response.cookies
            self.config.requests[self.website].cookie = cookie
            self.sessions[threading_id].cookies = cookie
        return response.json()


class RequestsDownloader(BaseDownloader):
    """Requests下载器"""

    def __init__(self, config: UserSpecificConfig,website:str):
        super().__init__(config)
        self.sessions:list[requests.Session] = []
        self.responses:list[requests.Response|None] = []
        self.website = website.capitalize()
        requests_config = self.config.requests[self.website]
        self.timeout = requests_config.timeout
        self.max_retry = requests_config.max_retry
        self.interval = requests_config.interval
        self.delay = requests_config.delay
        if not requests_config.headers:
            self.headers:dict[str, str] = field(default_factory=lambda:{
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive'
            })
        cookie = requests_config.cookie
        if cookie:
            self.headers['Cookie'] = cookie
        self._set_new_session()

    def _set_new_session(self):
        retry_strategy = Retry(
            total=3,
            backoff_factor=self.interval - 1,
            status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        template_session = requests.Session()
        template_session.mount("https://", adapter)
        for index in range(self.threading_number):
            self.responses.append(None)
            session = copy.deepcopy(template_session)
            self.sessions.append(session)

    def get(self, url, threading_id: int, retry: int = 0):
        """访问网站"""
        try:
            with ThreadingTimeout(self.timeout):
                response = self.sessions[threading_id].get(url, timeout=self.timeout)
            self.responses[threading_id] = response
            time.sleep(random.uniform(*self.delay))
        except TimeoutError:
            if retry <= self.max_retry:
                self.get(url, threading_id, retry + 1)

    def download(self, url: str, threading_id) -> str:
        """下载内容"""
        response = self.responses[threading_id]
        response.encoding = 'utf-8'
        if not self.sessions[threading_id].cookies:
            cookie = response.cookies
            self.config.requests[self.website].cookie = cookie
            self.sessions[threading_id].cookies = cookie
        return response.text