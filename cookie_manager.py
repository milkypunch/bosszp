import time
import random
import threading
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import verification

class CookieManager:
    def __init__(self,url):
        self.url = url
        self.cookies_list = []
        self.proxy = "http://127.0.0.1:7890"
        self.stop_event = threading.Event() #默认false


        # 设置 ChromeOptions
        self.chrome_options = Options()
        if self.proxy:
            self.chrome_options.add_argument(f'--proxy-server={self.proxy}')

        # 启动 Chrome WebDriver
        self.driver = webdriver.Chrome(options=self.chrome_options)

        self.driver = verification.main()
    # def login_and_get_token(self):
    #     # 这里添加登录逻辑，并获取 token
    #     self.driver.get(self.url)
    #     # 假设登录后 token 存储在 cookies 中
    #     cookies = self.driver.get_cookies()
    #     for cookie in cookies:
    #         if cookie['name'] == '__zp_stoken__':
    #             self.token = cookie['value']
    #             break
    #     if not self.token:
    #         raise ValueError("登录失败，未能获取 token")

    # def refresh_token(self):
    #     # 这里添加刷新 token 的逻辑
    #     # 例如，通过 API端点 请求刷新 token
    #     refresh_url = "http://www.zhipin.com/api/refresh_token"
    #     headers = {
    #         'Content-Type': 'application/json',
    #         'Authorization': f'Bearer {self.token}'
    #     }
    #     data = {
    #         'token': self.token
    #     }
    #     response = requests.post(refresh_url, headers=headers, json=data)
    #     if response.status_code == 200:
    #         self.token = response.json().get("token")
    #         print(f"Token 刷新成功: {self.token}")
    #     else:
    #         raise ValueError("刷新 token 失败")
        
    def cookie_generator(self, num_cookies=5):
        for _ in range(num_cookies):
            self.driver.get(self.url)
            cookies = self.driver.get_cookies() 
            # 每次获取一个包含多个 Cookie 的列表cookies
            yield cookies
            time.sleep(random.uniform(3, 5))  

    def set_cookies(self, cookies): # 为driver添加cookie
        self.driver.delete_all_cookies()
        for cookie in cookies:
            # 确保每个 Cookie 字典包含必要的键值对
            required_keys = {'name', 'value'}
            if not required_keys.issubset(cookie.keys()):
                raise ValueError(f"Cookie is missing required keys: {cookie}")
            self.driver.add_cookie(cookie)

    def refresh_cookies(self, interval=3600):
        while not self.stop_event.is_set(): # while not false
            for cookies in self.cookie_generator(num_cookies=1):
                self.cookies_list.append(cookies)
            self.stop_event.wait(interval)
            # 如果在等待期间（即 wait(interval) 方法调用期间）将 Event 对象的内部标志设置为 True，
            # wait() 方法会立即返回 True，从而立即循环到下一次检查 is_set() 时退出。

    def start_cookie_refresh_thread(self, interval=3600):
        self.cookie_refresh_thread = threading.Thread(target=self.refresh_cookies, args=(interval,))
        self.cookie_refresh_thread.start()

    def get_initial_cookies(self, num_cookies=5):
        for cookies in self.cookie_generator(num_cookies=num_cookies):
            self.cookies_list.append(cookies)

    def get_random_cookie(self):
        if not self.cookies_list:
            raise ValueError("No cookies available")
        return random.choice(self.cookies_list)
    
    #缺少validate_cookies & clean_expired_cookies
    
    def stop(self):
        self.stop_event.set() #True
        self.cookie_refresh_thread.join() # self.cookie_refresh_thread:实例变量
        self.driver.quit()
    # 设置 cookie_refresh_thread.daemon = True 
    # 可以确保当主线程结束时，后台线程也会自动结束。



url = 'https://www.zhipin.com/shanghai/'
cookie_manager = CookieManager(url)
cookie_manager.get_initial_cookies(num_cookies=2)
print("Initial cookies retrieved:", cookie_manager.cookies_list)

# Start the cookie refresh thread
cookie_manager.start_cookie_refresh_thread(interval=10)  # Short interval for testing

# Wait for some time to allow the background thread to refresh cookies
time.sleep(30)  # Adjust sleep time based on the refresh interval

# Fetch a random cookie from the list
try:
    random_cookie = cookie_manager.get_random_cookie()
    print("Random cookie retrieved:", random_cookie)
except ValueError as e:
    print(e)

# Stop the CookieManager
cookie_manager.stop()

print("CookieManager stopped successfully.")
page_url='https://www.zhipin.com/wapi/zpgeek/search/joblist.json?scene=1&query=%E8%BF%90%E8%90%A5&city=101020100&experience=&payType=&partTime=&degree=&industry=&scale=&stage=&position=&jobType=&salary=&multiBusinessDistrict=&multiSubway=&page=1&pageSize=30'
import requests

cookie_string = '; '.join([f"{cookie['name']}={cookie['value']}" for cookie in random_cookie])
print(cookie_string)
headers = {
    'Cookie': cookie_string,
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# The URL you want to access
page_url = 'https://www.zhipin.com/wapi/zpgeek/search/joblist.json?scene=1&query=%E8%BF%90%E8%90%A5&city=101020100&experience=&payType=&partTime=&degree=&industry=&scale=&stage=&position=&jobType=&salary=&multiBusinessDistrict=&multiSubway=&page=1&pageSize=30'

# Make the request
response = requests.get(page_url, headers=headers)

# Check the response
if response.status_code == 200:
    print("Request successful!")
    print("Response data:", response.json())
else:
    print(f"Request failed with status code: {response.status_code}")
    print("Response text:", response.text)

