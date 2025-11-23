import re


def url_parse(url):
    """解析并格式化url"""
    if 'https://changdunovel.com/wap/' in url:  # 处理番茄小说的分享链接
        book_id = re.search(r"book_id=(\d+)", url).group(1)
        url = 'https://fanqienovel.com/page/' + book_id
        return url, "fanqie"
    if "https://magev6.if.qidian.com/h5/share" in url:  # 处理起点小说的分享链接
        book_id = re.search(r"bookld=(\d+)", url).group(1)
        url = 'https://www.qidian.com/book/' + book_id
        return url, "qidian"

    url = url.split("?")[0].strip()
    if 'https://fanqienovel.com/page/' in url:
        return url, "fanqie"
    elif 'https://www.qidian.com/book/' in url:
        return url, "qidian"
    elif "https://www.biqugequ.org" in url:
        return url, "biquge"
    else:
        return url, ""
