import random
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.proxy import Proxy, ProxyType
from fake_useragent import UserAgent

class BosszpScraper:
    def __init__(self, cookie_manager):
        self.proxy='http://127.0.0.1:7890'
        self.ua=UserAgent()
        self.cookie_manager = cookie_manager
        self.driver = None        
        self.start_url='https://www.zhipin.com/wapi/zpgeek/search/joblist.json?scene=1&query=%E8%BF%90%E8%90%A5&city=101020100&experience=&payType=&partTime=&degree=&industry=&scale=&stage=&position=&jobType=&salary=&multiBusinessDistrict=&multiSubway=&page=1&pageSize=30'

    def create_driver(self):
        options = webdriver.ChromeOptions()

        options.add_argument(f"user-agent={self.ua.random}")
        options.add_argument('--proxy-server=%s' % self.proxy)
        options.add_argument("--incognito")  # 启用无痕模式
        self.driver = webdriver.Chrome(options=options)
        return self.driver 
    
    def request_page(self,url,retries=3, timeout=60,class_name='job-list'):
        self.create_driver()
        cookies = self.cookie_manager.get_random_cookie()
        for cookie in cookies:
            self.driver.add_cookie(cookie)

        # 刷新页面以应用 Cookie
        self.driver.refresh()
        while retries > 0:
            try:
                self.driver.get(url)
                WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((By.CLASS_NAME, class_name))
                )
                print("页面加载成功")
                return driver
            except (TimeoutException, WebDriverException) as e:
                print(f"发生错误: {e}")
                retries -= 1
                print(f"重试剩余次数: {retries}")
                time.sleep(random.uniform(5, 10))  # 随机等待5到10秒后重试
                self.driver.quit()
                self.driver = self.create_driver()
                for cookie in cookies:
                    self.driver.add_cookie(cookie)
                self.driver.refresh()
        print("页面加载失败")
        self.driver.quit()
        return None
    def parse_job_list(self):
        driver=self.create_driver()
        driver=driver.get(self.start_url)
        page_source = driver.page_source
        # 提取 JSON 数据
        data = json.loads(page_source)
      
        job_list = data['zpData']['jobList']
        for item in job_list:
                yield {
                    "job_name": item.get("jobName"),
                    "job_area": item.get("areaDistrict"),
                    "salary": item.get("salaryDesc"),
                    "job_degree": item.get("jobDegree"),
                    "job_experience": item.get("jobExperience"),
                    # if none: ""
                    "days_per_week": item.get("daysPerWeekDesc"),
                    "least_month": item.get("leastMonthDesc"),
                    "cpn_name": item.get("brandName"),
                    "cpn_type": item.get("brandIndustry"),
                    "finance_stage": item.get("brandStageName"),
                    "cpn_scale": item.get("brandScaleName"),
                    "welfare": item.get("welfareList")
                }



    def get_all_pages(self, start_url):
        driver = self.request_page(start_url, class_name='job-list')
        if not driver:
            return

        while True:
            self.parse_job_list(driver)
            try:
                next_button = driver.find_element(By.CLASS_NAME, "next-page")
                if "disabled" in next_button.get_attribute("class"):
                    break
                next_button.click()
                time.sleep(random.uniform(5, 10))  # 随机等待5到10秒后继续
                WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "job-list"))
                )
            except Exception as e:
                print(f"无法找到下一页按钮: {e}")
                break

        driver.quit()

