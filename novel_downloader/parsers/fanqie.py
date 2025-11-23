import json
import re
import time

from novel_downloader import UserSpecificConfig
from novel_downloader.models import DownloadMode
from novel_downloader.models.novel import *
from novel_downloader.parsers.base import BaseParser
import requests
from bs4 import BeautifulSoup, Tag
from novel_downloader.core.downloader import ChromeDownloader, APIDownloader, RequestsDownloader


# 转码表
transcoding = {"58670": "0", "58413": "1", "58678": "2", "58371": "3", "58353": "4", "58480": "5", "58359": "6",
               "58449": "7", "58540": "8", "58692": "9", "58712": "a", "58542": "b", "58575": "c", "58626": "d",
               "58691": "e", "58561": "f", "58362": "g", "58619": "h", "58430": "i", "58531": "j", "58588": "k",
               "58440": "l", "58681": "m", "58631": "n", "58376": "o", "58429": "p", "58555": "q", "58498": "r",
               "58518": "s", "58453": "t", "58397": "u", "58356": "v", "58435": "w", "58514": "x", "58482": "y",
               "58529": "z", "58515": "A", "58688": "B", "58709": "C", "58344": "D", "58656": "E", "58381": "F",
               "58576": "G", "58516": "H", "58463": "I", "58649": "J", "58571": "K", "58558": "L", "58433": "M",
               "58517": "N", "58387": "O", "58687": "P", "58537": "Q", "58541": "R", "58458": "S", "58390": "T",
               "58466": "U", "58386": "V", "58697": "W", "58519": "X", "58511": "Y", "58634": "Z",
               "58611": "的", "58590": "一", "58398": "是", "58422": "了", "58657": "我", "58666": "不",
               "58562": "人", "58345": "在", "58510": "他", "58496": "有", "58654": "这", "58441": "个",
               "58493": "上", "58714": "们", "58618": "来", "58528": "到", "58620": "时", "58403": "大",
               "58461": "地", "58481": "为", "58700": "子", "58708": "中", "58503": "你", "58442": "说",
               "58639": "生", "58506": "国", "58663": "年", "58436": "着", "58563": "就", "58391": "那",
               "58357": "和", "58354": "要", "58695": "她", "58372": "出", "58696": "也", "58551": "得",
               "58445": "里", "58408": "后", "58599": "自", "58424": "以", "58394": "会", "58348": "家",
               "58426": "可", "58673": "下", "58417": "而", "58556": "过", "58603": "天", "58565": "去",
               "58604": "能", "58522": "对", "58632": "小", "58622": "多", "58350": "然", "58605": "于",
               "58617": "心", "58401": "学", "58637": "么", "58684": "之", "58382": "都", "58464": "好",
               "58487": "看", "58693": "起", "58608": "发", "58392": "当", "58474": "没", "58601": "成",
               "58355": "只", "58573": "如", "58499": "事", "58469": "把", "58361": "还", "58698": "用",
               "58489": "第", "58711": "样", "58457": "道", "58635": "想", "58492": "作", "58647": "种",
               "58623": "开", "58521": "美", "58609": "总", "58530": "从", "58665": "无", "58652": "情",
               "58676": "己", "58456": "面", "58581": "最", "58509": "女", "58488": "但", "58363": "现",
               "58685": "前", "58396": "些", "58523": "所", "58471": "同", "58485": "日", "58613": "手",
               "58533": "又", "58589": "行", "58527": "意", "58593": "动", "58699": "方", "58707": "期",
               "58414": "它", "58596": "头", "58570": "经", "58660": "长", "58364": "儿", "58526": "回",
               "58501": "位", "58638": "分", "58404": "爱", "58677": "老", "58535": "因", "58629": "很",
               "58577": "给", "58606": "名", "58497": "法", "58662": "间", "58479": "斯", "58532": "知",
               "58380": "世", "58385": "什", "58405": "两", "58644": "次", "58578": "使", "58505": "身",
               "58564": "者", "58412": "被", "58686": "高", "58624": "已", "58667": "亲", "58607": "其",
               "58616": "进", "58368": "此", "58427": "话", "58423": "常", "58633": "与", "58525": "活",
               "58543": "正", "58418": "感", "58597": "见", "58683": "明", "58507": "问", "58621": "力",
               "58703": "理", "58438": "尔", "58536": "点", "58384": "文", "58484": "几", "58539": "定",
               "58554": "本", "58421": "公", "58347": "特", "58569": "做", "58710": "外", "58574": "孩",
               "58375": "相", "58645": "西", "58592": "果", "58572": "走", "58388": "将", "58370": "月",
               "58399": "十", "58651": "实", "58546": "向", "58504": "声", "58419": "车", "58407": "全",
               "58672": "信", "58675": "重", "58538": "三", "58465": "机", "58374": "工", "58579": "物",
               "58402": "气", "58702": "每", "58553": "并", "58360": "别", "58389": "真", "58560": "打",
               "58690": "太", "58473": "新", "58512": "比", "58653": "才", "58704": "便", "58545": "夫",
               "58641": "再", "58475": "书", "58583": "部", "58472": "水", "58478": "像", "58664": "眼",
               "58586": "等", "58568": "体", "58674": "却", "58490": "加", "58476": "电", "58346": "主",
               "58630": "界", "58595": "门", "58502": "利", "58713": "海", "58587": "受", "58548": "听",
               "58351": "表", "58547": "德", "58443": "少", "58460": "克", "58636": "代", "58585": "员",
               "58625": "许", "58694": "稜", "58428": "先", "58640": "口", "58628": "由", "58612": "死",
               "58446": "安", "58468": "写", "58410": "性", "58508": "马", "58594": "光", "58483": "白",
               "58544": "或", "58495": "住", "58450": "难", "58643": "望", "58486": "教", "58406": "命",
               "58447": "花", "58669": "结", "58415": "乐", "58444": "色", "58549": "更", "58494": "拉",
               "58409": "东", "58658": "神", "58557": "记", "58602": "处", "58559": "让", "58610": "母",
               "58513": "父", "58500": "应", "58378": "直", "58680": "字", "58352": "场", "58383": "平",
               "58454": "报", "58671": "友", "58668": "关", "58452": "放", "58627": "至", "58400": "张",
               "58455": "认", "58416": "接", "58552": "告", "58614": "入", "58582": "笑", "58534": "内",
               "58701": "英", "58349": "军", "58491": "侯", "58467": "民", "58365": "岁", "58598": "往",
               "58425": "何", "58462": "度", "58420": "山", "58661": "觉", "58615": "路", "58648": "带",
               "58470": "万", "58377": "男", "58520": "边", "58646": "风", "58600": "解", "58431": "叫",
               "58715": "任", "58524": "金", "58439": "快", "58566": "原", "58477": "吃", "58642": "妈",
               "58437": "变", "58411": "通", "58451": "师", "58395": "立", "58369": "象", "58706": "数",
               "58705": "四", "58379": "失", "58567": "满", "58373": "战", "58448": "远", "58659": "格",
               "58434": "士", "58679": "音", "58432": "轻", "58689": "目", "58591": "条", "58682": "呢"}


def translate(en_text):  # 转换乱码
    if not en_text: return ''
    de_text = ''
    for index in en_text:
        t1 = ''
        try:
            t1 = transcoding[str(ord(index))]
        except KeyError:
            t1 = index
        finally:
            de_text += t1
    return de_text


def user_state(html):
    soup = BeautifulSoup(html, 'lxml')
    user_info_div = soup.find("div", class_="muye-header-right")
    if user_info_div:
        if user_info_div.find('img'):  # 有图片证明已登录
            user_state_code = 0
        else:
            user_state_code = -1
        if user_info_div.find('i', class_='user-content-vip'):  # 有vip图标时
            user_state_code = 1
    else:
        user_state_code = -1
    return user_state_code


# 通过html获取小说相关信息，基类
class FanqieForHtml(BaseParser):
    def __init__(self, config: UserSpecificConfig, downloader: ChromeDownloader | APIDownloader | RequestsDownloader):
        self.config = config
        self.html = ""
        self.downloader = downloader

    def parse_novel_info(self, url: str, threading_id, **kwargs) -> Novel:
        # 定位json起始和终点位置
        self.html = kwargs['html']
        start = self.html.find("window.__INITIAL_STATE__=") + len("window.__INITIAL_STATE__=")
        start_html = self.html[start:]
        end = start_html.find(")()")
        script = start_html[:end].strip()[:-1].strip()[:-1]

        json_data = json.loads(script)
        page_data = json_data.get('page', {})
        name = page_data.get("bookName", )
        author = page_data.get("author", )
        author_desc = page_data.get("description", )
        label_item_str = page_data.get("categoryV2", )
        label_item_list = json.loads(label_item_str)
        status = page_data.get("creationStatus", )
        label_list = []
        if status == 1:
            label_list.append("连载中")
        else:
            label_list.append("已完结")
        for label_item in label_item_list:
            label_list.append(label_item.get("Name", ))
        count_word = page_data.get("wordNumber", 0)
        last_update_of_title = page_data.get("lastChapterTitle", "")
        last_update_of_time = int(page_data.get("lastPublishTime", 0))
        abstract = page_data.get("abstract", )
        book_cover_url = page_data.get("thumbUri", )
        book_cover_data = requests.get(book_cover_url).content

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

        novel = Novel(url=url,
                      name=name,
                      author=author,
                      author_description=author_desc,
                      tags=label_list,
                      description=abstract,
                      count=count_word,
                      last_update_chapter=last_update_of_title,
                      last_update_time=last_update_of_time,
                      cover_image_data=book_cover_data,
                      config=novel_config)

        chapter_list_with_volume = json_data.get("page", ).get("chapterListWithVolume")
        for chapters_list in chapter_list_with_volume:
            for chapter_item in chapters_list:
                title = chapter_item["title"]
                chapter_url = 'https://fanqienovel.com/reader/' + chapter_item.get("itemId")
                first_pass_time = int(chapter_item.get("firstPassTime"))
                real_chapter_order = int(chapter_item.get("realChapterOrder"))
                volume_name = chapter_item.get("volume_name")
                chapter = Chapter(title=title,
                                  root=url,
                                  url=chapter_url,
                                  volume=volume_name,
                                  order=real_chapter_order,
                                  timestamp=first_pass_time)
                novel+=chapter
        return novel

    def parse_chapter_content(self, url, threading_id, novel: Novel, **kwargs) -> tuple[Novel, tuple[Chapter]]:

        # 定位json起始和终点位置
        self.html = kwargs['html']
        start = self.html.find("window.__INITIAL_STATE__=") + len("window.__INITIAL_STATE__=")
        start_html = self.html[start:]
        end = start_html.find(")()")
        script = start_html[:end].strip()[:-1].strip()[:-1]
        # json合法化
        script = script.replace('"libra":undefined', '"libra":"undefined"')
        json_data = json.loads(script)
        count = json_data.get("reader", ).get("chapterData", ).get("chapterWordNumber")
        update_timestamp = int(json_data.get("reader", ).get("chapterData", ).get("firstPassTime", ))
        parent_soup = BeautifulSoup(self.html, 'lxml')
        if parent_soup.find('div', class_='muye-to-fanqie'):  # 完整性检查
            integrity = False
        else:
            integrity = True
        # 减小范围以准确定位text和img
        html_content = str(parent_soup.find('div', class_='muye-reader-content noselect'))
        soup = BeautifulSoup(translate(html_content), 'lxml')
        img_counter = 0
        img_items = []

        """处理图片"""
        # 处理所有图片标签
        img_tags = soup.find_all('img')
        for img in img_tags:
            img_counter += 1
            group_id = img_counter

            # 获取图片描述
            picture_desc = ""
            parent = img.parent
            while parent and isinstance(parent, Tag):
                # 检查是否有pictureDesc兄弟元素
                if parent.name == 'div' and parent.get('data-fanqie-type') == 'image':
                    picture_desc_tag = parent.find('p', class_='pictureDesc')
                    if (picture_desc_tag and
                            isinstance(picture_desc_tag, Tag) and
                            picture_desc_tag.get('group-id') == str(group_id)):
                        picture_desc = picture_desc_tag.get_text(strip=True)
                        break

                # 检查当前元素是否有pictureDesc类
                if (parent.name == 'p' and
                        'pictureDesc' in (parent.get('class') or [])):
                    picture_desc = parent.get_text(strip=True)
                    break

                parent = parent.parent

            # 构建字典键
            if picture_desc:
                dict_key = f"({group_id}) {picture_desc}"
            else:
                dict_key = f"({group_id})"

            img_url = img.get('src', '')
            img_data = requests.get(img_url).content
            # 添加到图片元组
            img_items.append((dict_key,img_data))
            # 替换图片为指定文本 - 创建一个新的 NavigableString
            replacement_text = soup.new_string(f'<&!img?group_id={group_id}/!&>')
            img.replace_with(replacement_text)

        # 提取所有段落文本，保留<img>替换标记
        content_div = soup.find('div', class_='muye-reader-content')
        text_content = []
        if content_div:
            # 遍历所有元素
            for element in content_div.descendants:
                # 处理字符串元素
                if isinstance(element, str):
                    text = element.strip()
                    if text:
                        # 检查是否是图片替换标记
                        if text.startswith('<&!img?group_id=') and text.endswith('/!&>'):
                            text_content.append(text)
                        else:
                            text_content.append(text)

                # 处理标签元素
                elif isinstance(element, Tag) and element.name == 'p':
                    # 跳过图片描述段落
                    if 'pictureDesc' in (element.get('class') or []):
                        continue

                    text = element.get_text(strip=True)
                    if text:
                        text_content.append(text)

        text_content = [text_content[i] for i in range(0, len(text_content), 2)]  # 去除重复文本
        novel_content = "\n".join(text_content)
        if '已经是最新一章' in novel_content:
            novel_content = novel_content.replace('已经是最新一章', '')

        chapter = novel[url]
        # 赋值
        chapter.images = img_items
        chapter.count = count
        chapter.timestamp = update_timestamp
        chapter.content = novel_content
        chapter.is_complete = integrity
        novel+=chapter
        return novel, (chapter,)


class FanqieForBrowser(FanqieForHtml):

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


class FanqieForOiapi(BaseParser):
    def __init__(self, config: UserSpecificConfig, downloader: APIDownloader):
        self.config = config
        self.downloader = downloader

    def parse_chapter_content(self, url, threading_id, novel, **kwargs) -> tuple[Novel, tuple[Chapter|None]]:
        # 形参url无用
        index = len(novel.chapters)+1
        page_url = novel.url
        # 以POST获取内容
        post_data = {
            "chapter": index,
            "id": re.search(r'page/(\d+)', page_url).group(1),
            "key": self.downloader.key,
            "type": "json"
        }
        self.downloader.get(url="https://oiapi.net/api/FqRead", threading_id=threading_id,post_data=post_data)
        response = self.downloader.download(url=page_url, threading_id=threading_id)
        message = response['message']
        data = response.get('data')
        # 没有键data说明出现问题
        if not data:
            if message == "请检测章节选择是否正确":
                return novel,(None,)
            raise ValueError(f"oiapi出现错误\nmessage:{message}")
        else:

            chapter_data = data[0]
            title = chapter_data['chapter_title']
            volume = chapter_data['volume']
            update_time: int = chapter_data['time']  # 更新时间
            count_word: int = chapter_data['word_number']  # 章节字数
            content = chapter_data['content']  # 小说内容
            if '已经是最新一章' in content:
                content = content.replace('已经是最新一章', '')

            chapter = Chapter(title=title,
                              root=page_url,
                              url=url,
                              order=index,
                              volume=volume,
                              content=content,
                              timestamp=update_time,
                              count=count_word,
                              is_complete=True)
            novel+=chapter
            return novel, (chapter,)

    def parse_novel_info(self, url, threading_id, **kwargs) -> Novel:

        # 以POST获取内容
        post_data = {
            "chapter": 0,
            "id": re.search(r'page/(\d+)', url).group(1),
            "key": self.downloader.key,
            "type": "json"
        }

        self.downloader.get("https://oiapi.net/api/FqRead", post_data=post_data, threading_id=threading_id)
        response=self.downloader.download("https://oiapi.net/api/FqRead", threading_id=threading_id)
        message = response['message']
        data = response.get('data', )
        # 没有键data说明出现问题
        if not data:
            raise ValueError(f"oiapi出现错误\nmessage:{message}")
        else:
            book_cover_data = requests.get(data.get('thumb', )).content
            name = data.get('title')
            author = data.get('author')
            word_number = int(data.get('word_number'))
            # 更新小说信息
            config = self.downloader.api_config
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
                          name=name,
                          author=author,
                          author_description=None,
                          count=word_number,
                          description=data.get('docs'),
                          cover_image_data=book_cover_data,
                          config=novel_config)
            return novel


class FanqieForReq(FanqieForHtml):
    def __init__(self, config: UserSpecificConfig, downloader: RequestsDownloader):
        super().__init__(config, downloader)

    def parse_chapter_content(self, url, threading_id, novel, **kwargs):
        self.downloader.get(url, threading_id=threading_id)
        html = self.downloader.download(url, threading_id=threading_id)
        return super().parse_chapter_content(url, threading_id=threading_id, html=html, novel=novel)
    def parse_novel_info(self, url: str, threading_id, **kwargs):
        self.downloader.get(url, threading_id=threading_id)
        html = self.downloader.download(url, threading_id=threading_id)
        user_state(html)
        return super().parse_novel_info(url, threading_id=threading_id, html=html)


class FanqieParser(BaseParser):
    def __init__(self, config: UserSpecificConfig, downloader: ChromeDownloader | APIDownloader | RequestsDownloader):
        self.config = config
        self.downloader = downloader
        if self.config.get_mode == DownloadMode.BROWSER:
            self._parser = FanqieForBrowser(self.config, self.downloader)
        elif self.config.get_mode == DownloadMode.API:
            self._parser = FanqieForOiapi(self.config, self.downloader)
        elif self.config.get_mode == DownloadMode.REQUESTS:
            self._parser = FanqieForReq(self.config, self.downloader)

    def parse_novel_info(self, url: str, threading_id, **kwargs) -> Novel:
        return self._parser.parse_novel_info(url, threading_id=threading_id)

    def parse_chapter_content(self, url, threading_id, novel: Novel, **kwargs) -> tuple[Novel, tuple[Chapter, ...]]:
        return self._parser.parse_chapter_content(url=url, threading_id=threading_id, novel=novel)
