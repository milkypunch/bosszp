import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import time
import random
import csv
from selenium.common.exceptions import TimeoutException
from login_automation import LoginInitiator, LoginHandler


def get_job_info(job_card, driver):

        
        job_name = job_card.find("span", class_="job-name").text.strip()
        job_area = job_card.find("span", class_="job-area").text.strip()
        salary = job_card.find("span", class_="salary").text.strip()
        
        # 提取工作年限和学历
        tag_list_li = job_card.find("div", class_="job-info clearfix").find("ul", class_="tag-list").find_all('li')
        if len(tag_list_li)<3:
            work_year_period = tag_list_li[0].text.strip() if len(tag_list_li) > 0 else ""
            education = tag_list_li[1].text.strip() if len(tag_list_li) > 1 else ""

        # if: avoid indexError
        else:
            work_year_period = " ".join([li.text.strip() for li in tag_list_li[:2]])
            education = tag_list_li[2].text.strip()
        ### 有些结构不是这样（实习生），按工作经验把它筛选掉


        # 提取公司信息
        company_info = job_card.find("div", class_="company-info")
        cpn_name = company_info.find("h3", class_="company-name").text.strip()
        company_tags = company_info.find("ul", class_="company-tag-list")
        cpn_type = company_tags.find_all("li")[0].text.strip() if len(company_tags.find_all("li")) > 0 else ""
        finance_stage = company_tags.find_all("li")[1].text.strip() if len(company_tags.find_all("li")) > 1 else ""
        cpn_size = company_tags.find_all("li")[2].text.strip() if len(company_tags.find_all("li")) > 2 else ""
        
        # 提取福利信息
        benefits = job_card.find("div", class_="info-desc").text.strip() if job_card.find("div", class_="info-desc") else ""
        
        # 调试信息：打印 job_card 的内容
        print(f"Job card HTML: {job_card.prettify()}")
        

        return {
            "job_name": job_name,
            "job_area": job_area,
            "salary": salary,
            "experience_or_duration": work_year_period,
            "education": education,
            "cpn_name": cpn_name,
            "cpn_type": cpn_type,
            "finance_stage": finance_stage,
            "cpn_size": cpn_size,
            "benefits": benefits,
            # "job_desc": job_desc
        }



def main():
    try:
        login_initiator = LoginInitiator()
        login_initiator.start_server()
        driver = login_initiator.open_website_and_click_login()
        if driver is None:
            print("Failed to open website and click login.")
            return
        phone_numbers = ["15579327821", "13879397711"]
        login_handler = LoginHandler(driver, phone_numbers)
        login_handler.input_phone_and_click_button()
        login_handler.run()

        # 登录成功后，继续进行爬取操作
        # 等待工作卡片加载完成
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "job-card-wrapper"))
        )
        print("页面加载成功")
        
        # 使用 BeautifulSoup 解析页面
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        job_cards = soup.find_all("li", class_="job-card-wrapper")  # 返回一个列表
        print(f"Found {len(job_cards)} job cards")

        # 提取职位信息
        jobs = []
        for job_card in job_cards:
            job_info = get_job_info(job_card, driver)  # 返回一个字典
            jobs.append(job_info)
        
        # 打印或保存职位信息
        for job in jobs:
            print(job)
        
    except Exception as e:
        print(f"An error occurred: {e}")
        # 保持浏览器打开以便调试
        input("Press Enter to close the browser...")

if __name__ == "__main__":
    main()