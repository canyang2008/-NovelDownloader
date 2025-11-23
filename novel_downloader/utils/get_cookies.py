from DrissionPage import Chromium,ChromiumOptions
def get_cookies(user_data_dir=None):
    co = ChromiumOptions().set_user_data_path(user_data_dir)
    driver = Chromium(addr_or_opts=co)
    tab = driver.get_tab()
    tab.get("https://fanqienovel.com")
    cookies = tab.cookies()
    cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
    print(cookie_str)