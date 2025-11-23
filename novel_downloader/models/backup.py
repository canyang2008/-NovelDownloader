from dataclasses import dataclass


@dataclass
class BackupConfig:
    """备份配置"""
    auto: bool = False
    auto_save_method: str = "T:86400"
    dir: str = "C:\\"
    name: str = "Novel_backup <User> <T:'%Y-%m-%d'>.zip"
    last_time: int = -1
    pop_up_folder: bool = True
    max_backups: int = 10