
import requests
import random
import time
from fake_useragent import UserAgent
from cookie_manager import CookieManager


class JobScraper:
    def __init__(self,cookie_manager):
        self.cookie_manager = cookie_manager
        self.proxy = 'http://127.0.0.1:7890'
        self.ua = UserAgent()


    def create_session(self):
        session = requests.Session()
        session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'application/json, text/plain, */*',
            'Connection': 'keep-alive'
        })
        if self.proxy:
            session.proxies.update({
                'http': self.proxy,
                'https': self.proxy
            })
        return session

    def request_page(self, url, retries=3, timeout=60):
        # while retries > 0:
        session = self.create_session()
        #     cookies = self.cookie_manager.get_random_cookie() if self.cookie_manager else []

        #     # 添加 Cookie 到会话
        #     for cookie in cookies:
        #         session.cookies.set(cookie['name'], cookie['value'])

        try:
            response = session.get(url, timeout=timeout)
            response.raise_for_status()  # 检查请求是否成功
            return response.json()
        except (requests.exceptions.RequestException, Exception) as e:
            print(f"发生错误: {e}")
        #         retries -= 1
        #         print(f"重试剩余次数: {retries}")

                
        #         # 随机等待5到10秒后重试
        #         time.sleep(random.uniform(5, 10))
                
        #     finally:
        #         # 确保无痕
        #         session.cookies.clear()
        
        # print("页面加载失败")
        # return None
url = "https://www.zhipin.com/wapi/zpgeek/search/joblist.json?scene=1&query=%E8%BF%90%E8%90%A5&city=101020100&experience=&payType=&partTime=&degree=&industry=&scale=&stage=&position=&jobType=&salary=&multiBusinessDistrict=&multiSubway=&page=1&pageSize=30"
# cookie_manager = CookieManager(url)
# cookie_manager.start_cookie_refresh_thread(interval=3600) # 后台线程
# cookie_manager.get_initial_cookies(num_cookies=5) # 主线程

scraper=JobScraper()
response=scraper.request_page(url)
print(response)