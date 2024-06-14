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

class LoginInitiator:
    def __init__(self):
        self.proxy = 'http://127.0.0.1:7890'
        # self.ua = UserAgent()
        options = webdriver.ChromeOptions()
        # options.add_argument(f"user-agent={self.ua.random}")
        options.add_argument('--proxy-server=%s' % self.proxy)
        # options.add_argument("--incognito")  # 启用无痕模式
        self.driver = webdriver.Chrome(options=options)
        self.driver.set_window_size(1200, 800)

    def start_server(self):
        server_thread = threading.Thread(target=server.run_server)
        server_thread.daemon = True
        server_thread.start()
        return server_thread

    def open_website_and_click_login(self, url = "https://www.zhipin.com/"):
        self.driver.get(url)
        time.sleep(3)  # 等待页面加载

        # 分情况
        elements_1 = self.driver.find_elements(By.XPATH, '//a[@ka="header-login"]')
        elements_2 = self.driver.find_elements(By.XPATH, '//a[@href="/web/user/" and @ka="m_job_index_signup"]/div[text()="登录/注册"]')

        # 判断并赋值 login_link
        if elements_1:
            login_link = elements_1[0]

        elif elements_2:
            login_link = elements_2[0]
        
        else:
            print("Neither element is present.")
        # 移动鼠标并点击登录链接
        ActionChains(self.driver).move_to_element(login_link).perform()
        time.sleep(1)  # 模拟人类移动鼠标的延迟
        login_link.click()
        time.sleep(3)  # 等待页面加载
        return self.driver

class LoginHandler:
    def __init__(self, driver, phone_numbers):
        self.driver = driver
        self.phone_numbers = phone_numbers
        self.current_phone_index = 0

    def input_phone_and_click_button(self, phone_number=None):

        if phone_number is None:
            phone_number = self.phone_numbers[self.current_phone_index]
        
        time.sleep(3)
        # 点击输入手机号
        phone_input = self.driver.find_element(By.XPATH, '//input[@type="tel" and @placeholder="手机号"]')
        ActionChains(self.driver).move_to_element(phone_input).perform()
        time.sleep(1)  # 模拟人类移动鼠标的延迟
        phone_input.click()

        # 清空输入框
        phone_input.clear()

        # 模拟人类逐字输入手机号
        for digit in phone_number:
            phone_input.send_keys(digit)
            time.sleep(random.uniform(0.2, 0.5))  # 每输入一个字符后等待随机时间

        # 移动鼠标并点击发送验证码
        send_code_button = self.driver.find_element(By.XPATH, '//div[@ka="send_sms_code_click"]')
        ActionChains(self.driver).move_to_element(send_code_button).perform()
        time.sleep(1)  # 模拟人类移动鼠标的延迟
        send_code_button.click()
        time.sleep(3)


        try:
            # 等待元素加载完成
            verify_button = WebDriverWait(self.driver, 8).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="yidun_intelli-tips"]'))
            )
        except TimeoutException:
            try:
                verify_button = WebDriverWait(self.driver, 8).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@class="geetest_wait"]/span[@class="geetest_wait_dot geetest_dot_2"]'))
                )
            except TimeoutException:
                verify_button = None

        if verify_button:
            try:
                # 移动到元素并暂停
                ActionChains(self.driver).move_to_element(verify_button).perform()
                time.sleep(1)  # 模拟人类移动鼠标的延迟
                # 点击元素
                self.driver.execute_script("arguments[0].click();", verify_button)
            except (ElementNotInteractableException, TimeoutException) as e:
                print(f"Error: {e}")
        else:
            print("No verify buttons found.")
        time.sleep(3)

    def check_and_switch_phone_number(self):
        self.input_phone_and_click_button()
        try:
            phone_input = self.driver.find_element(By.XPATH, '//input[type="tel" and placeholder="手机号"]')
        except NoSuchElementException:
            print("手机号输入框被拼图遮挡，退出函数")
            return
        
        current_value = phone_input.get_attribute('value')
        if current_value:
            print(f"输入框中已有手机号: {current_value}")
            # 切换手机号
            self.current_phone_index = (self.current_phone_index + 1) % len(self.phone_numbers)
            print(f"Switching to phone number: {self.phone_numbers[self.current_phone_index]}")
            # 清空输入框
            phone_input.clear()
            # 调用 input_phone_and_click_button 函数
            self.input_phone_and_click_button(self.phone_numbers[self.current_phone_index])


    def handle_img(self, path):
        img = cv2.imread(path)
        imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 1)
        imgCanny = cv2.Canny(imgBlur, 60, 60)
        imgEqualized = cv2.equalizeHist(imgCanny)
        return imgEqualized

    def locate_and_match_puzzle(self):
        # 定义滑块和目标模板的路径
        slider2_template_path = '/Users/milkypunch/Downloads/slider_template2.png'
        target_template_path = '/Users/milkypunch/Downloads/target_template10.png'

        # 处理滑块和目标位置的模板图像
        slider2_template = self.handle_img(slider2_template_path)
        target_template = self.handle_img(target_template_path) 

        # 截图并保存
        screenshot_path = '/Users/milkypunch/Desktop/screenshot.png'
        self.driver.save_screenshot(screenshot_path)

        # 处理截图
        screenshot_img = self.handle_img(screenshot_path)

        # 定位滑块
        res_slider2 = cv2.matchTemplate(screenshot_img, slider2_template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc_slider = cv2.minMaxLoc(res_slider2)

        # 读取验证背景图
        img_element = self.driver.find_element(By.CSS_SELECTOR, 'img.yidun_bg-img')
        img_url = img_element.get_attribute('src')
        response = requests.get(img_url)
        image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        img_path = '/Users/milkypunch/Desktop/background.jpg'
        cv2.imwrite(img_path, image)

        # 处理背景图
        bkg = self.handle_img(img_path)

        # 定位缺口
        res_target = cv2.matchTemplate(bkg, target_template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc_target = cv2.minMaxLoc(res_target)

        top_left = max_loc_target
        w, h = 82, 84
        bottom_right = (top_left[0] + w, top_left[1] + h)
        cv2.rectangle(bkg, top_left, bottom_right, 255, 2)
        cv2.imwrite('matched_image.png', bkg)
        cv2.imshow('Matched Image', bkg)
        cv2.waitKey(5000)
        cv2.destroyAllWindows()

        target_position = max_loc_target[0] / 480 * 676 / 2 - 3
        return target_position

    def ease_out_bounce(self, x):
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

    def ease_in_out_bounce(self, x):
        return (1 - self.ease_out_bounce(1 - 2 * x)) / 2 if x < 0.5 else (1 + self.ease_out_bounce(2 * x - 1)) / 2

    def get_tracks_by_time(self, distance, duration, ease_func):
        tracks = []
        offsets = []
        start_time = time.time()
        end_time = start_time + duration
        current_time = start_time

        while current_time < end_time:
            elapsed_time = current_time - start_time
            ease = getattr(self, ease_func)
            offset = round(ease(elapsed_time / duration) * distance)
            if offsets:
                tracks.append(offset - offsets[-1])
            else:
                tracks.append(offset)
            offsets.append(offset)
            current_time = time.time()
            time.sleep(0.02)  # 控制时间间隔，确保平滑移动

        tracks.append(distance - sum(tracks))
        return tracks

    def move_slider(self, slider, puzzle_element, target_position):
        def get_element_position(element):
            return element.location['x'] - 551

        current_position = get_element_position(puzzle_element)
        distance = target_position - current_position

        action = ActionChains(self.driver)
        action.click_and_hold(slider).perform()

        while abs(distance) > 1:
            if abs(distance) < 10:
                duration = 0.5
                tracks = self.get_tracks_by_time(distance, duration, 'ease_in_out_bounce')
            else:
                duration = 1
                tracks = self.get_tracks_by_time(distance, duration, 'ease_in_out_bounce')

            for track in tracks:
                action.move_by_offset(track, 0).perform()
                time.sleep(0.02)
                current_position = get_element_position(puzzle_element)
                distance = target_position - current_position
                if abs(distance) < 1:
                    break

            current_position = get_element_position(puzzle_element)
            distance = target_position - current_position

        action.pause(0.2).release(slider).perform()
        time.sleep(3)

    def check_sms_sent(self):
        try:
            elements = self.driver.find_elements(By.CSS_SELECTOR, 'div[ka="send_sms_code_click"].btn-sms.sending')
            if elements:
                for element in elements:
                    if '已发送' in element.text: 
                        time.sleep(15) # 快捷指令
                        response = requests.get("http://localhost:8000/get_latest_code")
                        response.raise_for_status()  # 如果状态码不是 200，会抛出 HTTPError 异常
                        sms_code = response.json().get("code")
                        if sms_code:
                            return sms_code
            time.sleep(1)
        except NoSuchElementException:
            time.sleep(1)
        return None

    def check_slider2_exists(self):
        try:
            slider = self.driver.find_element(By.XPATH, '//span[@class="yidun_slider__icon"]')
            return slider
        except NoSuchElementException:
            return None

    def enter_sms_code(self, sms_code):
        time.sleep(3)
        sms_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@type="text" and @ka="signup-sms"]'))
        )
        ActionChains(self.driver).move_to_element(sms_input).perform()
        time.sleep(1)
        sms_input.click()

        for digit in sms_code:
            sms_input.send_keys(digit)
            time.sleep(random.uniform(0.2, 0.5))

    def run(self):

        max_attempts = 10
        attempts = 0
        else_attempts = 0

        while attempts < max_attempts:
            sms_code = self.check_sms_sent()
            if sms_code:
                self.enter_sms_code(sms_code)
                break

            slider = self.check_slider2_exists()
            if slider:
                puzzle_element = self.driver.find_element(By.CSS_SELECTOR, 'img.yidun_jigsaw')
                target_position = self.locate_and_match_puzzle()
                self.move_slider(slider, puzzle_element, target_position)

                sms_code = self.check_sms_sent()
                if sms_code:
                    self.enter_sms_code(sms_code)
                    break

                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, 'span.yidun_tips__text.yidun-fallback__tip')
                    for element in elements:
                        if '点击' in element.text and '重试' in element.text:
                            time.sleep(2)
                            ActionChains(self.driver).move_to_element(element).perform()
                            element.click()
                            continue
                except Exception as e:
                    print("An error occurred:", e)
            else:
                time.sleep(random.uniform(60, 70))
                self.driver.refresh()
                self.check_and_switch_phone_number()

                else_attempts += 1
                if else_attempts % 5 == 0:
                    self.current_phone_index = (self.current_phone_index + 1) % len(self.phone_numbers)
                    print(f"Switching to phone number: {self.phone_numbers[self.current_phone_index]}")
                    self.input_phone_and_click_button(self.phone_numbers[self.current_phone_index])


            attempts += 1

        if attempts == max_attempts:
            print("达到最大尝试次数，未能成功发送短信")

        agree_policy_checkbox = self.driver.find_element(By.XPATH, '//input[@type="checkbox" and @class="agree-policy"]')
        ActionChains(self.driver).move_to_element(agree_policy_checkbox).perform()
        time.sleep(random.uniform(3, 5))
        agree_policy_checkbox.click()

        time.sleep(random.uniform(3, 5))

        login_button = self.driver.find_element(By.XPATH, '//button[@type="submit" and @ka="signup_submit_button_click"]')
        ActionChains(self.driver).move_to_element(login_button).perform()
        time.sleep(random.uniform(3, 5))
        login_button.click()

        WebDriverWait(self.driver, 8).until(
        EC.presence_of_element_located((By.XPATH, '//a[@ka="header-home"]'))
        )

        if self.driver.current_url == "https://www.zhipin.com/web/geek/job-recommend":
            print("登录成功")
        else:
            print("登录失败")

        # 模拟鼠标移动并点击首页链接
        home_link = self.driver.find_element(By.XPATH, '//a[@ka="header-home"]')
        ActionChains(self.driver).move_to_element(home_link).perform()
        time.sleep(random.uniform(3, 5))  # 模拟人类移动鼠标的延迟
        home_link.click()

        # 等待页面加载
        WebDriverWait(self.driver, 8).until(
            EC.presence_of_element_located((By.XPATH, '//input[@type="text" and @name="query"]'))
        )

        # 模拟鼠标移动并点击职位类型框
        search_input = self.driver.find_element(By.XPATH, '//input[@type="text" and @name="query"]')
        ActionChains(self.driver).move_to_element(search_input).perform()
        time.sleep(random.uniform(3, 5))  # 模拟人类移动鼠标的延迟
        search_input.click()

        # 输入“运营”
        for char in "运营":
            search_input.send_keys(char)
            time.sleep(0.5)

        # 模拟鼠标移动并点击搜索按钮
        search_button = self.driver.find_element(By.XPATH, '//button[@class="btn btn-search" and @ka="search_box_index"]')
        ActionChains(self.driver).move_to_element(search_button).perform()
        time.sleep(random.uniform(3, 5))  # 模拟人类移动鼠标的延迟
        search_button.click()

        # 在加载页面的时候关了

        # 等待页面加载
        # time.sleep(5)
            
        # return self.driver


# def main():
#     try:
#         login_initiator = LoginInitiator()
#         login_initiator.start_server()
#         driver = login_initiator.open_website_and_click_login()
#         if driver is None:
#             print("Failed to open website and click login.")
#             return
#         phone_numbers = ["15579327821", "13879397711"]
#         login_handler = LoginHandler(driver, phone_numbers)
#         login_handler.input_phone_and_click_button()
#         login_handler.run()
#     except Exception as e: # 没有抛出异常
#         print(f"An error occurred: {e}")
#         # 保持浏览器打开以便调试
#         input("Press Enter to close the browser...")
    

# if __name__ == "__main__":
#     main()
