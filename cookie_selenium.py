import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from fake_useragent import UserAgent

class BosszpScraper:
    def __init__(self):
        self.proxy = 'http://127.0.0.1:7890'
        self.ua = UserAgent()
        self.driver = None        
        self.start_url = 'https://www.zhipin.com/wapi/zpgeek/search/joblist.json?scene=1&query=%E8%BF%90%E8%90%A5&city=101020100&experience=&payType=&partTime=&degree=&industry=&scale=&stage=&position=&jobType=&salary=&multiBusinessDistrict=&multiSubway=&page=1&pageSize=30'

    def create_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument(f"user-agent={self.ua.random}")
        options.add_argument('--proxy-server=%s' % self.proxy)
        options.add_argument("--incognito")  # 启用无痕模式
        self.driver = webdriver.Chrome(options=options)
        return self.driver 

    # def get_cookies(self):
    #     return self.driver.get_cookies()

    # def set_cookies(self, cookies):
    #     for cookie in cookies:
    #         self.driver.add_cookie(cookie)

    def request_page(self, url, retries=3, timeout=60, class_name='job-list'):
        self.create_driver()
        self.driver.get(url)
        # cookies = self.get_cookies()

        while retries > 0:
            try:
                self.driver.get(url)
                WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.CLASS_NAME, class_name))
                )
                print("页面加载成功")
                print(self.driver.page_source)
                return self.driver
            except (TimeoutException, WebDriverException) as e:
                print(f"发生错误: {e}")
                retries -= 1
                print(f"重试剩余次数: {retries}")
                time.sleep(random.uniform(5, 10))  # 随机等待5到10秒后重试
                self.driver.quit()
                self.driver = self.create_driver()
                self.driver.get(url)
                # self.set_cookies(cookies)
                self.driver.refresh()
        print("页面加载失败")
        self.driver.quit()
        return None

# 示例使用
scraper = BosszpScraper()
scraper.request_page(scraper.start_url)
