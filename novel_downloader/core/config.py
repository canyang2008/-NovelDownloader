import json
import os
import time

import ijson
from novel_downloader.models.config import *
from novel_downloader.models.group import GroupConfig
from novel_downloader.models.novel import Config as NovelConfig
from novel_downloader.models.save import JsonSaveConfig, TxtSaveConfig, HtmlSaveConfig, RootSaveConfig
from novel_downloader.models.user import GlobalUserConfig, UserConfig

class ConfigManagerForUnion:
    """配置管理器"""

    def __init__(self):
        self.global_config = GlobalUserConfig()
        self.config = UserSpecificConfig()
        self.load_config()

    def load_config(self):
        """加载配置文件"""
        with open("data/Local/manage.json", "r", encoding="utf-8") as f:
            user_config = json.load(f)
        """解析全局配置数据"""
        self.global_config.version = user_config.get("VERSION", "1.1.0")
        self.global_config.readme = user_config.get("README", "")
        self.global_config.current_user = user_config.get("USER", "Default")

        # 解析用户配置
        users_data = user_config.get("USERS", {})
        for username, user_data in users_data.items():
            self.global_config.users[username] = UserConfig(
                user_config_path=user_data.get("User_config_path", ""),
                user_data_dir=user_data.get("User_data_dir", ""),
                base_dir=user_data.get("Base_dir", "")
            )
        config_file = self.global_config.users[self.global_config.current_user].user_config_path
        group_file = os.path.join(self.global_config.users[self.global_config.current_user].base_dir, "mems.json")
        self._parse_config(config_file)
        self._parse_group(group_file)


    def _parse_config(self, config_file:str):
        """解析原始配置数据"""
        with open(config_file, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
        # 基础字段
        self.config.version = raw_data.get("Version", "1.1.0")
        self.config.user_name = self.global_config.current_user  # 使用当前用户名
        self.config.group = raw_data.get("Group", "Default")
        self.config.readme = raw_data.get("README", "")
        self.config.play_completion_sound = raw_data.get("Play_completion_sound", False)
        self.config.get_mode = raw_data.get("Get_mode", 0)
        self.config.threading_number = raw_data.get("Threads_num", 3)
        match self.config.get_mode:
            case 0:
                self.config.get_mode = DownloadMode.BROWSER
            case 1:
                self.config.get_mode = DownloadMode.API
            case 2:
                self.config.get_mode = DownloadMode.REQUESTS

        # 浏览器配置
        browser_data = raw_data.get("Browser", {})

        # 获取用户特定的浏览器数据目录
        user_data_dir = self.global_config.users[self.global_config.current_user].user_data_dir

        self.config.browser = BrowserConfig(
            timeout=browser_data.get("Timeout", 10),
            max_retry=browser_data.get("Max_retry", 3),
            interval=browser_data.get("Interval", 2.0),
            delay=browser_data.get("Delay", [1.0, 1.5]),
            port=browser_data.get("Port", 9445),
            headless=browser_data.get("Headless", False),
            user_data_dir=user_data_dir,  # 使用用户特定的数据目录
            site_states=browser_data.get("State", {})
        )

        # API配置
        api_data = raw_data.get("Api", {})
        for site, site_config in api_data.items():
            option = site_config.get("Option", "")
            providers = {}

            # 解析每个API配置
            for provider_name, provider_config in site_config.items():
                if provider_name != "Option":
                    providers[provider_name] = ApiProviderConfig(
                        name=provider_name,
                        max_retry=provider_config.get("Max_retry", 3),
                        timeout=provider_config.get("Timeout", 10),
                        interval=provider_config.get("Interval", 2.0),
                        delay=provider_config.get("Delay", [1.0, 3.0]),
                        key=provider_config.get("Key", ""),
                        endpoint=provider_config.get("Endpoint", ""),
                        headers=provider_config.get("Headers", {}),
                        params=provider_config.get("Params", {}),
                        enabled=provider_config.get("Enabled", True)
                    )

            self.config.api[site] = SiteApiConfig(option=option, providers=providers)

        # Requests配置
        requests_data = raw_data.get("Requests", {})
        for site, site_config in requests_data.items():
            self.config.requests[site] = SiteRequestsConfig(
                max_retry=site_config.get("Max_retry", 3),
                timeout=site_config.get("Timeout", 10),
                interval=site_config.get("Interval", 2.0),
                delay=site_config.get("Delay", [1.0, 3.0]),
                cookie=site_config.get("Cookie", ""),
                headers=site_config.get("Headers", {}),
                proxies=site_config.get("Proxies", {})
            )

        # 保存方法配置

        base_dir = self.global_config.users[self.global_config.current_user].base_dir
        save_data = raw_data.get("Save_method", {})
        self.config.save_method = SaveMethodConfig(
            json=JsonSaveConfig(**save_data.get("json", {})),
            txt=TxtSaveConfig(**save_data.get("txt", {})),
            html=HtmlSaveConfig(**save_data.get("html", {})),
            root=RootSaveConfig()
        )

        # 备份配置
        backup_data = raw_data.get("Backup", {})
        self.config.backup = BackupConfig(
            auto=backup_data.get("Auto", False),
            auto_save_method=backup_data.get("Auto_save_method", "T:86400"),
            dir=backup_data.get("Dir", "C:\\"),
            name=backup_data.get("Name", "Novel_backup <User> <T:'%Y-%m-%d'>.zip"),
            last_time=backup_data.get("Last_time", -1),
            pop_up_folder=backup_data.get("Pop_up_folder", True)
        )

        # 未处理项目
        self.config.unprocess = raw_data.get("Unprocess", [])

    def _parse_group(self, group_file):
        """解析分组配置数据"""
        with open(group_file, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
        self.config.groups = GlobalGroupConfig()
        self.config.groups.version = raw_data.get("Version", "1.1.0")
        self.config.groups.current_group = self.config.group
        for group in raw_data.keys():
            if group not in ["Version"]:
                group_config = GroupConfig()
                group_config.group_name = group
                for url, name in raw_data[group].items():
                    novel_path = os.path.join(os.path.dirname(group_file), f"{name}.json")
                    if os.path.exists(novel_path):
                        with open(novel_path, "r", encoding="utf-8") as f:
                            saved_config = ijson.items(f, "config")
                            saved_config = next(saved_config, {})
                            # 保存方法配置
                            hash_ = saved_config.get("Hash", str(abs(hash(name))))
                            save_data = saved_config.get("Save_method", {})
                            save_method = SaveMethodConfig(
                                json=JsonSaveConfig(**save_data.get("json", {})),
                                txt=TxtSaveConfig(**save_data.get("txt", {})),
                                html=HtmlSaveConfig(**save_data.get("html", {})),
                                root=RootSaveConfig()
                            )
                            novel_config = NovelConfig(hash=hash_)
                            novel_config.version = saved_config.get("Version", "1.1.0")
                            novel_config.url = url
                            novel_config.name = name
                            novel_config.group = group
                            novel_config.max_retry = saved_config.get("Max_retry", 3)
                            novel_config.timeout = saved_config.get("Timeout", 10)
                            novel_config.interval = saved_config.get("Interval", 2)
                            novel_config.delay = saved_config.get("Delay", [1.0, 3.0])
                            novel_config.save_method = save_method
                            novel_config.first_time = saved_config.get("First_time_stamp", -1)
                            group_config.members.append(novel_config)
                    else:group_config.members.append(None)
                self.config.groups.groups[group] = group_config

    def set_collection(self):
        """设置集合"""
        pass