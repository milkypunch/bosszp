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

class Test():
    def __init__(self):
        self.proxy='http://127.0.0.1:7890'
        self.ua=UserAgent()
      
        self.driver = None        

    def create_driver(self):
        options = webdriver.ChromeOptions()

        options.add_argument(f"user-agent={self.ua.random}")
        options.add_argument('--proxy-server=%s' % self.proxy)
        options.add_argument("--incognito")  # 启用无痕模式
        self.driver = webdriver.Chrome(options=options)
        return self.driver 
    
    def request_page(self,url='https://www.zhipin.com/job_detail/674c54ddcb01441a1HZ_39q-FVVY.html?lid=9tj5KPqj68f.search.1&securityId=WqM6B0OkUegdw-P17TYTFKXTlq9MRgGbUi-TXFl-N0sXeqp5DJFDl0jP9jg6jt6vzkzLSuhD9PDRYTqYBLz6qZ_hQRJjwF-cVdtNB-l6ZCahTeM7NSQqH7aMF1RBKnmypFhNu5OYYMfWLKz_oScQkfM~&sessionId=',retries=3, timeout=60):
        self.create_driver()
        self.driver.get(url)
        page_source = self.driver.page_source
        print(page_source)

test=Test()
test.request_page()
