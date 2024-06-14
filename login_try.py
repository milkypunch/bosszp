import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
from selenium.common.exceptions import ElementNotInteractableException, TimeoutException


# 初始化WebDriver
driver = webdriver.Chrome()  # 或者使用其他浏览器驱动，例如webdriver.Firefox()
driver.set_window_size(1200, 800)

# 打开网页
driver.get("https://www.zhipin.com/")

# 等待页面加载
time.sleep(3)

# 移动鼠标并点击登录链接
login_link = driver.find_element(By.XPATH, '//a[@ka="header-login"]')
ActionChains(driver).move_to_element(login_link).perform()
time.sleep(1)  # 模拟人类移动鼠标的延迟
login_link.click()

# 等待页面加载
time.sleep(3)

# 点击输入手机号
phone_input = driver.find_element(By.XPATH, '//input[@type="tel" and @placeholder="手机号"]')
ActionChains(driver).move_to_element(phone_input).perform()
time.sleep(1)  # 模拟人类移动鼠标的延迟
phone_input.click()

# 模拟人类逐字输入手机号
phone_number = "15579327821"
for digit in phone_number:
    phone_input.send_keys(digit)
    time.sleep(random.uniform(0.2, 0.5))  # 每输入一个字符后等待随机时间

# 移动鼠标并点击发送验证码
send_code_button = driver.find_element(By.XPATH, '//div[@ka="send_sms_code_click"]')
ActionChains(driver).move_to_element(send_code_button).perform()
time.sleep(1)  # 模拟人类移动鼠标的延迟
send_code_button.click()

# time.sleep(100) #查看元素
# time.sleep(3)
# verify_buttons = driver.find_elements(By.XPATH, '//div[@class="yidun_intelli-tips"]') or driver.find_elements(By.XPATH, '//div[@class="geetest_ring"]/div[@class="geetest_small"]')
# verify_button = verify_buttons[0]
# ActionChains(driver).move_to_element(verify_button).perform()
# time.sleep(1)  # 模拟人类移动鼠标的延迟

# verify_button.click()

time.sleep(3)
verify_buttons = driver.find_elements(By.XPATH, '//div[@class="yidun_intelli-tips"]')

if not verify_buttons:
    verify_buttons = driver.find_elements(By.XPATH, '//div[@class="geetest_wait"]/span[@class="geetest_wait_dot geetest_dot_2"]')
    # <div class="geetest_wait"><span class="geetest_wait_dot geetest_dot_1">
    # </span><span class="geetest_wait_dot geetest_dot_2"></span><span class="geetest_wait_dot geetest_dot_3"></span></div>
#'//div[@class="geetest_ring"]/div[@class="geetest_small"]')
# <span class="geetest_radar_tip_content">点击按钮进行验证</span>
# '//span[@class="geetest_wait_dot geetest_dot_2"]'
# <span class="geetest_wait_dot geetest_dot_2"></span>
if verify_buttons:
    verify_button = verify_buttons[0]
    
    try:

        # 移动到元素并暂停
        ActionChains(driver).move_to_element(verify_button).perform()
        time.sleep(1)  # 模拟人类移动鼠标的延迟
        

        
        # 点击元素
        verify_button.click()
    except (ElementNotInteractableException, TimeoutException) as e:
        print(f"Error: {e}")
else:
    print("No verify buttons found.")

### 也有可能不要拼图 直接发送验证码
### 也可能是另一种拼图
time.sleep(60)

import cv2
import numpy as np

# 等待页面加载完成
time.sleep(2)

# 截图并保存
screenshot_path = '/Users/milkypunch/Desktop/screenshot.png'
driver.save_screenshot(screenshot_path)

# 读取截图
image = cv2.imread(screenshot_path)

# 截图尺寸 2400*1322
height, screen_width = image.shape[:2]
print(f"Screenshot dimensions: {screen_width} x {height}")

#bkg = driver.<img class="yidun_bg-img" alt="验证码背景" style="border-radius: 2px" src="https://necaptcha.nosdn.127.net/e2293b5a81eb4105987993eec5e42835@2x.jpg">
# <img class="yidun_jigsaw" alt="验证码滑块" src="https://necaptcha.nosdn.127.net/18c4ef93e1734581a9fecf9710c3dcd6@2x.png" style="left: 0px;">

# 读取验证背景图
img_element = driver.find_element(By.CSS_SELECTOR, 'img.yidun_bg-img')
img_url = img_element.get_attribute('src')
print("Image URL:", img_url)
response = requests.get(img_url)
img_path = '/Users/milkypunch/Desktop/background.jpg'
# 将图像保存到本地
with open(img_path, 'wb') as file:
    file.write(response.content)

# 使用 OpenCV 读取图像
bkg = cv2.imread(img_path, 0)

# 尺寸 480*240
height, bkg_width = image.shape[:2]
print(f"Background dimensions: {bkg_width} x {height}")


# 定义滑块和目标模板的路径
slider_template_paths = [
    '/Users/milkypunch/Downloads/slider_template.png',
    '/Users/milkypunch/Downloads/slider_template2.png',
]

target_template_paths = [
    # '/Users/milkypunch/Downloads/target_template1.png',
    # '/Users/milkypunch/Downloads/target_template2.png',
    # '/Users/milkypunch/Downloads/target_template3.png',
    # '/Users/milkypunch/Downloads/target_template4.png',
    # '/Users/milkypunch/Downloads/target_template5.png',
    # '/Users/milkypunch/Downloads/target_template6.png',
    # '/Users/milkypunch/Downloads/target_template7.png',
    # '/Users/milkypunch/Downloads/target_template8.png',
    # '/Users/milkypunch/Downloads/target_template9.png',
    # '/Users/milkypunch/Downloads/target_template10.png',
    '/Users/milkypunch/Downloads/target_template11.png',
    # '/Users/milkypunch/Downloads/target_template12.png'
]

# 读取滑块和目标位置的模板图像
slider_templates = [cv2.imread(path, 0) for path in slider_template_paths]
target_templates = [cv2.Canny(cv2.imread(path, 0), 50, 150) for path in target_template_paths]

# 转换截图为灰度图像
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# 对图像进行边缘检测
edges_image = cv2.Canny(gray_image, 50, 150)

# 初始化最佳匹配变量
best_slider_match_val = -1  # 滑块的最佳匹配值
best_slider_match_loc = None
best_target_match_val = -1  # 目标的最佳匹配值
best_target_match_loc = None

# 遍历所有滑块模板图像，找到最佳匹配 Best slider match location: (1104, 1078)
for slider_template in slider_templates:
    res_slider = cv2.matchTemplate(gray_image, slider_template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc_slider = cv2.minMaxLoc(res_slider)

    if max_val > best_slider_match_val:
        best_slider_match_val = max_val
        best_slider_match_loc = max_loc_slider


# 遍历所有缺口模板图像，找到最佳匹配
for target_template in target_templates:
    res_target = cv2.matchTemplate(cv2.Canny(bkg, 50, 150), target_template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc_target = cv2.minMaxLoc(res_target)
    
    if max_val > best_target_match_val:
        best_target_match_val = max_val
        best_target_match_loc = max_loc_target

# 计算滑块需要拖动的距离 [0]是x坐标的值
drag_distance = best_target_match_loc[0]*(screen_width/bkg_width) - best_slider_match_loc[0]


# 打印匹配结果以验证
print(f"Best slider match location: {best_slider_match_loc}")
print(f"Best target match location: {best_target_match_loc}")
print(f"Drag distance: {drag_distance}")

# 定位滑块元素
slider = driver.find_element(By.XPATH, 
                             '//span[@class="yidun_slider__icon"]')

# 创建ActionChains对象
actions = ActionChains(driver)

# 点击并按住滑块
actions.click_and_hold(slider).perform()

# 模拟分段拖动滑块
steps = 20
for i in range(steps):
    actions.move_by_offset(drag_distance / steps, 0).perform()
    time.sleep(random.uniform(0.02, 0.05))  # 添加一些延迟以模拟更自然的拖动行为


# 释放滑块
actions.release().perform()

# 等待一段时间以确保验证完成
time.sleep(1)

###对准缺口不成功 会重新开启拼图验证


# 等待45秒
time.sleep(45)

# 暂停脚本，等待用户手动输入验证码
sms_code = input("请输入收到的验证码: ")

# 点击输入框并输入验证码
sms_input = driver.find_element(By.XPATH, '//input[@type="text" and @ka="signup-sms"]')
ActionChains(driver).move_to_element(sms_input).perform()
time.sleep(1)  # 模拟人类移动鼠标的延迟
sms_input.click()
for digit in sms_code:
    sms_input.send_keys(digit)
    time.sleep(random.uniform(0.1, 0.3))  # 每输入一个字符后等待随机时间

# 移动鼠标并点击同意用户协议
agree_policy_checkbox = driver.find_element(By.XPATH, '//input[@type="checkbox" and @class="agree-policy"]')
ActionChains(driver).move_to_element(agree_policy_checkbox).perform()
time.sleep(1)  # 模拟人类移动鼠标的延迟
agree_policy_checkbox.click()

# 移动鼠标并点击登录/注册按钮
login_button = driver.find_element(By.XPATH, '//button[@type="submit" and @ka="signup_submit_button_click"]')
ActionChains(driver).move_to_element(login_button).perform()
time.sleep(1)  # 模拟人类移动鼠标的延迟
login_button.click()

# 等待页面跳转
time.sleep(5)

# 确认是否跳转到登录后的页面
if driver.current_url == "https://www.zhipin.com/web/geek/job-recommend":
    print("登录成功")
else:
    print("登录失败")

# 关闭浏览器
driver.quit()

##到达推荐页面，应该点击首页图标，到达