from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

def clear_browser_data(driver):
    # Open the settings page for clearing browsing data
    driver.get("chrome://settings/clearBrowserData")
    
    # Wait for the settings page to load
    driver.implicitly_wait(5)
    
    # Clear cookies
    driver.find_element(By.XPATH, '//settings-ui').send_keys(Keys.ENTER)
    
    # Alternatively, you can use JavaScript to clear cache and cookies
    driver.execute_script("window.localStorage.clear();")
    driver.execute_script("window.sessionStorage.clear();")
    driver.execute_script("caches.keys().then(function(names) { for (let name of names) caches.delete(name); });")
    
    # Clear cookies using WebDriver's method
    driver.delete_all_cookies()

# 设置 ChromeOptions
chrome_options = Options()
# 添加代理设置（如果有）
proxy = "http://127.0.0.1:7890"
if proxy:
    chrome_options.add_argument(f'--proxy-server={proxy}')

# 启动 Chrome WebDriver
driver = webdriver.Chrome(options=chrome_options)

# 打开一个网页
driver.get("https://playground.insnail.ai/#/")

# 清除浏览器数据
clear_browser_data(driver)

# 继续执行其他操作或关闭浏览器
driver.quit()
