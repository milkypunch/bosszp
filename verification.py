import requests
import cv2
import numpy as np
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from fake_useragent import UserAgent
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import ElementNotInteractableException, TimeoutException, NoSuchElementException
import threading
import server

def start_server():
    server_thread = threading.Thread(target=server.run_server)
    server_thread.daemon = True
    server_thread.start()
    return server_thread

# 启动服务器
server_thread = start_server()

# proxy='http://127.0.0.1:7890'
# ua=UserAgent()

# options = webdriver.ChromeOptions()

# options.add_argument(f"user-agent={ua.random}")
# options.add_argument('--proxy-server=%s' % proxy)
# options.add_argument("--incognito")  # 启用无痕模式
# driver = webdriver.Chrome(options=options)
driver = webdriver.Chrome()
driver.set_window_size(1200, 800)

# driver.get('https://www.zhipin.com/web/user/')
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

def input_phone_and_click_button(driver):

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

    time.sleep(3)


    try:
        # 等待元素加载完成
        verify_button = WebDriverWait(driver, 8).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="yidun_intelli-tips"]'))
        )
    except TimeoutException:
        try:
            verify_button = WebDriverWait(driver, 8).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="geetest_wait"]/span[@class="geetest_wait_dot geetest_dot_2"]'))
            )
        except TimeoutException:
            verify_button = None

    if verify_button:
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

    time.sleep(3)

input_phone_and_click_button(driver)

def handle_img(path):
    img = cv2.imread(path)
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 1)
    # imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 0)
    imgCanny = cv2.Canny(imgBlur, 60, 60)
    # imgCanny = cv2.Canny(imgBlur, 50, 150)
    imgEqualized = cv2.equalizeHist(imgCanny)

    return imgEqualized


# 定义滑块和目标模板的路径
# slider1_template_path = '/Users/milkypunch/Downloads/slider_template.png'
slider2_template_path = '/Users/milkypunch/Downloads/slider_template2.png'

target_template_path = '/Users/milkypunch/Downloads/target_template10.png'

# 处理滑块和目标位置的模板图像

slider2_template = handle_img(slider2_template_path)
target_template = handle_img(target_template_path) 



# 检查是否存在 slider1/2 的元素
# slider1_elements = driver.find_elements(By.XPATH, '//div[@class="geetest_slider_button"]')

slider2_elements = driver.find_elements(By.XPATH, '//span[@class="yidun_slider__icon"]')


def locate_and_match_puzzle(driver, target_template):
    # 截图并保存
    screenshot_path = '/Users/milkypunch/Desktop/screenshot.png'
    driver.save_screenshot(screenshot_path)

    # 处理截图
    screenshot_img = handle_img(screenshot_path)

    # 截图尺寸 2400*1322
    height, screen_width = screenshot_img.shape[:2]
    print(f"Screenshot dimensions: {screen_width} x {height}")

    # 定位滑块
    res_slider2 = cv2.matchTemplate(screenshot_img, slider2_template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc_slider = cv2.minMaxLoc(res_slider2)

    # 读取验证背景图
    img_element = driver.find_element(By.CSS_SELECTOR, 'img.yidun_bg-img')
    img_url = img_element.get_attribute('src')
    print("Image URL:", img_url)
    # 从 URL 获取图像
    response = requests.get(img_url)
    image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    # 将图像保存到本地
    img_path = '/Users/milkypunch/Desktop/background.jpg'
    cv2.imwrite(img_path, image)

    # 处理背景图
    bkg = handle_img(img_path)

    # 尺寸 480*240
    height, bkg_width = bkg.shape[:2]
    print(f"Background dimensions: {bkg_width} x {height}")

    # 定位缺口
    res_target = cv2.matchTemplate(bkg, target_template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc_target = cv2.minMaxLoc(res_target)

    # 查看匹配定位情况        
    top_left = max_loc_target
    w, h = 82, 84
    bottom_right = (top_left[0] + w, top_left[1] + h)
    
    cv2.rectangle(bkg, top_left, bottom_right, 255, 2)
    cv2.imwrite('matched_image.png',bkg)
    cv2.imshow('Matched Image', bkg)
    cv2.waitKey(5000)
    cv2.destroyAllWindows()

    target_position = max_loc_target[0] / 480 * 676 / 2 - 3
    # 拼图左边缘初始位置距离背景图边缘：3
    print(f"Best slider match location: {max_loc_slider}")
    print(f"Best target match location: {max_loc_target}")
    print(f"Drag distance: {target_position}")

    return target_position
    

# if slider1_elements:
#     print("Using slider1")
    

#     # 遍历滑块1模板图像，找到最佳匹配
#     res_slider1 = cv2.matchTemplate(screenshot_img, slider1_template, cv2.TM_CCOEFF_NORMED)
#     _, max_val, _, max_loc_slider = cv2.minMaxLoc(res_slider1)

#     if max_val > best_slider_match_val:
#         best_slider_match_val = max_val
#         best_slider_match_loc = max_loc_slider

#     # 遍历所有缺口模板图像，找到最佳匹配
#     target_template_paths = [
#     '/Users/milkypunch/Downloads/target_template1.png',
#     '/Users/milkypunch/Downloads/target_template2.png',
#     '/Users/milkypunch/Downloads/target_template3.png',
#     '/Users/milkypunch/Downloads/target_template4.png',
#     '/Users/milkypunch/Downloads/target_template5.png',
#     '/Users/milkypunch/Downloads/target_template6.png',
#     '/Users/milkypunch/Downloads/target_template7.png',
#     '/Users/milkypunch/Downloads/target_template8.png',
#     '/Users/milkypunch/Downloads/target_template9.png',
#     ]

#     for target_template in target_templates:
#         res_target = cv2.matchTemplate(screenshot_img, target_template, cv2.TM_CCOEFF_NORMED)
#         _, max_val, _, max_loc_target = cv2.minMaxLoc(res_target)
        
#         if max_val > best_target_match_val:
#             best_target_match_val = max_val
#             best_target_match_loc = max_loc_target


#     top_left = max_loc_target
#     w, h = 101, 87
#     bottom_right = (top_left[0] + w, top_left[1] + h)

    
#     cv2.rectangle(screenshot_img, top_left, bottom_right, 255, 2)
#     cv2.imwrite('matched_image.png',screenshot_img)
#     cv2.imshow('Matched Image', screenshot_img)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()
#     # 定位滑块元素
#     slider = driver.find_element(By.XPATH, '//div[@class="geetest_slider_button"]')
#     # 计算滑块需要拖动的距离
#     # 截图2400，窗口1200
#     drag_distance = (best_target_match_loc[0] - best_slider_match_loc[0])/2

    



# else:
#     pass

# slider = driver.find_element(By.XPATH, '//span[@class="yidun_slider__icon"]')
# puzzle_element = driver.find_element(By.CSS_SELECTOR, 'img.yidun_jigsaw')
# 96.88*255.5

def ease_out_bounce(x):
    n1 = 7.5625
    d1 = 2.75
    if x < 1 / d1:
        return n1 * x * x
    elif x < 2 / d1:
        x -= 1.5 / d1
        return n1 * x * x + 0.75
    elif x < 2.5 / d1:
        x -= 2.25 / d1
        return n1 * x * x + 0.9375
    else:
        x -= 2.625 / d1
        return n1 * x * x + 0.984375

def ease_in_out_bounce(x):
    return ( 1 - ease_out_bounce( 1 - 2 * x ) ) / 2 if x < 0.5 else ( 1 + ease_out_bounce( 2 * x - 1 ) ) / 2

def get_tracks_by_time(distance, duration, ease_func):
    tracks = []
    offsets = []
    start_time = time.time()
    end_time = start_time + duration
    current_time = start_time

    while current_time < end_time:
        elapsed_time = current_time - start_time
        ease = globals()[ease_func]
        offset = round(ease(elapsed_time / duration) * distance)
        # distance/time
        if offsets:
            tracks.append(offset - offsets[-1])
        else:
            tracks.append(offset)
        offsets.append(offset)
        current_time = time.time()
        time.sleep(0.02)  # 控制时间间隔，确保平滑移动

    # 确保最后一个位置是目标位置
    tracks.append(distance - sum(tracks))
    return tracks

def move_slider(slider, puzzle_element, target_position, driver):
    def get_element_position(element):
        return element.location['x'] - 551
    # 背景图左边缘 - 窗口左边缘 = 552

    current_position = get_element_position(puzzle_element)
    distance = target_position - current_position

    action = ActionChains(driver)
    action.click_and_hold(slider).perform()

    while abs(distance) > 1:  # 允许一定的误差范围
        if abs(distance) < 10:
            # 微调阶段
            duration = 0.5  # 微调阶段的持续时间
            tracks = get_tracks_by_time(distance, duration, 'ease_in_out_bounce')
        else:
            # 正常移动阶段
            duration = 1  # 正常移动阶段的持续时间
            tracks = get_tracks_by_time(distance, duration, 'ease_in_out_bounce')

        # 这里的 for 循环是在 if-else 语句块之后执行的
        for track in tracks:
            action.move_by_offset(track, 0).perform()
            time.sleep(0.02)  # 控制时间间隔，确保平滑移动

            # 调试输出当前滑块位置和目标位置
            current_position = get_element_position(puzzle_element)
            print(f"Current position: {current_position}, Target position: {target_position}")

            distance = target_position - current_position
            if abs(distance) < 1:
                break

        current_position = get_element_position(puzzle_element)
        distance = target_position - current_position


    # 松开滑块
    action.pause(0.2).release(slider).perform()
    time.sleep(3)

# import pika

# def send_message(message: str):
#     # 1. 连接到 RabbitMQ 服务器
#     connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    
#     # 2. 创建一个频道
#     channel = connection.channel()
    
#     # 3. 声明一个队列
#     channel.queue_declare(queue='sms_queue', durable=True)
    
#     # 4. 发送消息到队列
#     channel.basic_publish(
#         exchange='',
#         routing_key='sms_queue',
#         body=message,
#         properties=pika.BasicProperties(
#             delivery_mode=2,  # make message persistent
#         ))
    
#     # 5. 关闭连接
#     connection.close()

def check_sms_sent(driver):
    # while True:
    try:
        elements = driver.find_elements(By.CSS_SELECTOR, 'div[ka="send_sms_code_click"].btn-sms.sending')
        if elements:
            for element in elements:
                if '已发送' in element.text:
                    print('已发送短信:', element.text)
                    
                    time.sleep(15) # 等快捷指令
                    # 从服务器获取验证码
                    response = requests.get("http://localhost:8000/get_latest_code")
                    if response.status_code == 200:
                        sms_code = response.json().get("code")
                        if sms_code:
                            # send_message(sms_code)
                            return sms_code
        time.sleep(1)  # 等待一秒后再检查
    except NoSuchElementException:
        time.sleep(1)  # 等待一秒后再检查
    return None

def check_slider2_exists(driver):
    try:
        slider = driver.find_element(By.XPATH, '//span[@class="yidun_slider__icon"]')
        return slider
    except NoSuchElementException:
        return None

def enter_sms_code(driver, sms_code):
    """
    点击输入框并输入验证码

    :param driver: Selenium WebDriver 实例
    :param sms_code: 要输入的验证码
    """
    time.sleep(3)
    sms_input = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, '//input[@type="text" and @ka="signup-sms"]'))
)
    ActionChains(driver).move_to_element(sms_input).perform()
    time.sleep(1)  # 模拟人类移动鼠标的延迟
    sms_input.click()
    
    for digit in sms_code:
        sms_input.send_keys(digit)
        time.sleep(random.uniform(0.2, 0.5))  # 每输入一个字符后等待随机时间

max_attempts = 10
attempts = 0

while attempts < max_attempts:

    # 检查是否已发送验证码
    sms_code = check_sms_sent(driver)
    if sms_code:
        print("成功发送短信并输入验证码")
        enter_sms_code(driver, sms_code)
        break

    # 检查 slider2 是否存在
    slider = check_slider2_exists(driver)
    if slider:
        puzzle_element = driver.find_element(By.CSS_SELECTOR, 'img.yidun_jigsaw')
        # 96.88*255.5
        target_position = locate_and_match_puzzle(driver, target_template)
        move_slider(slider, puzzle_element, target_position, driver) 
        
        sms_code = check_sms_sent(driver)
        if sms_code:
            print("成功发送短信并输入验证码")
            enter_sms_code(driver, sms_code)
            break

         # 检查是否存在失败提示
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, 'span.yidun_tips__text.yidun-fallback__tip')
            for element in elements:
                # 检查元素的文本内容是否包含“点击”和“重试”
                if '点击' in element.text and '重试' in element.text:
                    # element without text will return ''
                    
                    time.sleep(2)
                    ActionChains(driver).move_to_element(element).perform()
                    element.click()
                    print("检测到失败提示，点击重试按钮")
                    continue  # 跳过当前循环的剩余部分，并立即开始下一次循环
        except Exception as e:
            print("An error occurred:", e)

    else:
        # slider2 不存在，刷新页面
        print("未找到 slider，刷新页面") #在这要
        time.sleep(60)  # 等待一段时间后重试

        driver.refresh()
        input_phone_and_click_button(driver)

    attempts += 1

if attempts == max_attempts:
    print("达到最大尝试次数，未能成功发送短信")


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

def main():
    return driver

if __name__ == "__main__":
    main()


# 关闭浏览器
# driver.quit()

##到达推荐页面
##跳转到爬虫页面


