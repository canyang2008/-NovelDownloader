import json
import re


def txt_cut(file_path:str = r"E:\Administartor\Document\FanQieNovel-Downloader\NovelDownloader2.0\src\data\Bookstore\Canyang\Default\学姐别怕，我来保护你\学姐别怕，我来保护你.json"):
    with open(file_path,"r",encoding="utf-8") as f:
        json_data = json.load(f)
    novel_info = json_data['info']
    novel_name = novel_info['name']
    novel_abstract = novel_info['abstract'].replace('\n', '\n\t')
    info_text = (  # 生成小说信息文本
            f"小说名：{novel_name}\n作者：{novel_info['author']}\n"
            f"简介：{novel_abstract}\n标签：{novel_info['label']}\n"
            f"字数：{novel_info['count_word']}\n最后更新：{novel_info['last_update']}\n"
            f"链接：{novel_info['url']}\n\n"
        )
    chapters = json_data['chapters']
    text = ""
    id_ = 2
    chapter_list = list(chapters.values())
    title_list = list(chapters.keys())
    range_chapter_list = chapter_list[607:]
    range_title_list = title_list[607:]
    for title,chapter in zip(range_title_list,range_chapter_list):
        content = re.sub(r'<&!img\?group_id=\d+/!&>', '', chapter['content'])  # 去掉图片占位字符串
        formatted = (  # 格式化文本
            f"{title}\n    "
            f"{chapter['count_word']}    "
            f"{chapter['update']}\n\n"
            f"{content}\n\n"
        )
        text += formatted
        if len(text.encode("utf-8")) > 3800*1024:
            with open(f"{novel_name} part{id_}.txt","w",encoding="utf-8") as f:
                f.write(text)
            text = ""
            id_ += 1
txt_cut()