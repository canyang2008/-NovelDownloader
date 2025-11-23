import os
from pathlib import Path

import platform

def dir_transform(path:str, user, group, name):  # 特殊路径转化
    path = path.replace('<User>',user) if '<User>' in path else path
    path = path.replace('<Group>',group) if '<Group>' in path else path
    path = path.replace('<Name>',name) if '<Name>' in path else path
    file_dir = os.path.basename(os.path.basename(path))
    
    system = platform.system()
    if system != "Windows":
        normalized = file_dir.replace('\\', '/')  # Linux目录的特殊处理
    else:normalized = path
    file_dir = str(Path(normalized))
    return file_dir
