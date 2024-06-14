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
# import pandas as pd


# driver get start_url -> get all pages(for loop) -> get job cards from each page&get next page(return bool) -> get job info->get jobs from page->get all pages




class BosszpScraper():
    def __init__(self):
        self.base_url='https://www.zhipin.com'
        self.start_url = "https://www.zhipin.com/web/geek/job?query=%E8%BF%90%E8%90%A5&city=101020100" 
        # 换API
   


    def get_job_info(self,job_card, driver):

        
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
        
        try:
            job_link = job_card.find("a", class_="job-card-left")["href"]
            job_link = "https://www.zhipin.com" + job_link
            # 调试信息：打印 job_link
            print(f"Job link: {job_link}")
        except (AttributeError, TypeError) as e:
            print(f"Error extracting job link: {e}")
            job_link = ""
        


        # 获取职位描述信息
        job_desc = self.get_job_description(job_link, driver) if job_link else ""
        

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
            "job_desc": job_desc
        }

    # def create_driver():
    #     options = webdriver.ChromeOptions()
    #     options.add_argument('--headless')  # 启用无头模式
    #     options.add_argument('--disable-gpu')
    #     options.add_argument('--no-sandbox')
    #     options.add_argument('--disable-dev-shm-usage')
    #     driver = webdriver.Chrome(options=options)

    #     return driver

    # url是get_job_info传入的 
    def get_job_description(self,job_link, driver):
    
        print(f"Fetching job description from URL: {job_link}")
        
        retries = 3
        while retries > 0:
            try:
                driver.get(job_link)
                # 检查是否出现 security-check 页面
                # if "security-check" in driver.page_source:
                #     print("Security check detected, waiting for user to complete it...")
                #     time.sleep(120)  # 等待用户完成 security-check

                # 等待职位描述加载完成
                WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "job-sec-text"))
                )
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                job_desc_div = soup.find("div", class_="job-sec-text")
                if job_desc_div:
                    job_desc = job_desc_div.get_text(separator="\n").strip()
                    return job_desc
            except Exception as e:
                print(f"Error waiting for job description: {e}")
                retries -= 1
                time.sleep(5)  # 等待5秒后重试
                # 重新启动浏览器
                # driver.quit()
                # driver = create_driver()
        return "" 

    def get_jobs_from_page(self,url, driver):

        print(f"Fetching URL: {url}")
        retries = 3
        while retries > 0:
            try:
                driver.get(url)
                # 等待工作卡片加载完成
                WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.CLASS_NAME, "job-card-wrapper"))
            )
                print("页面加载成功")
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                job_cards = soup.find_all("li", class_="job-card-wrapper") #return a list
                print(f"Found {len(job_cards)} job cards")
                jobs = []
                for job_card in job_cards:
                    job_info = self.get_job_info(job_card, driver) # dict
                    jobs.append(job_info)
                
                return jobs, soup # 为什么要返回soup：避免重复解析
            except TimeoutException as e:
                print(f"等待工作卡片超时: {e}")
            except Exception as e:
                print(f"发生错误: {e}")
        retries -= 1
        print(f"重试剩余次数: {retries}")
        time.sleep(random.uniform(3, 5))  
        print("页面加载失败")
        driver.quit()
        return None
        # 模拟滚动页面 <- 需要滚动才需要获得完整页面的时候
        #why not
        # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # time.sleep()  # 随机等待时间
        


    def get_previous_page_url(driver, page_number):
        # 构建前一页的URL
        previous_page_number = page_number - 1
        if previous_page_number < 1:
            return None  # 如果前一页页码小于1，返回None

        previous_url = f"https://www.zhipin.com/web/geek/job?query=%E8%BF%90%E8%90%A5&city=101020100&page={previous_page_number}"
        driver.get(previous_url)
        time.sleep(random.uniform(2, 5))  # 在跳转页面后 程序暂停执行时间
        return driver.current_url



    def get_next_page_url(driver, page_number):

        try:
            # 构建XPath表达式，查找包含页码的按钮
            next_page_button = driver.find_element(By.XPATH, f"//a[text()='{page_number}']")
            if 'disabled' in next_page_button.get_attribute('class'):
                return False
            else:
                driver.execute_script("arguments[0].click();", next_page_button) #此处执行点击下一页按钮，改变driver
                time.sleep(random.uniform(2, 5))  # 在点击页码后 程序暂停执行时间
                return driver.current_url
        except Exception as e:
            print(f"No page {page_number} found or error clicking page {page_number}: {e}")
            previous_url = get_previous_page_url(driver, page_number)
            if previous_url:
                return get_next_page_url(driver, page_number)  # 递归调用，继续尝试翻页
            else:
                return False
            
                
        
    ##我想不断爬，直到在最后一页的下一页button class为disabled

    

    def scrape_all_jobs(self):
        driver = webdriver.Chrome()
        # driver = create_driver()  # 确保chromedriver在系统路径中
        driver.get(self.start_url)#打开页面
        
        all_jobs = []#yield修改
        page = 1

        while True:
            print(f"正在爬取第 {page} 页")
            jobs, soup = self.get_jobs_from_page(driver.current_url, driver) #current_url:只读，只用来获取
            all_jobs.extend(jobs) #jobs:list -- yield
            page += 1

            next_page_url = self.get_next_page_url(driver, page)
            if not self.get_next_page_url(driver, page):
                break
        
        driver.quit()
        return all_jobs
scraper=BosszpScraper()
all_jobs=scraper.scrape_all_jobs()
print(all_jobs)

    # def save_jobs_to_csv(jobs, filename):
    #     keys = jobs[0].keys()
    #     with open(filename, 'w', newline='', encoding='utf-8') as output_file:
    #         dict_writer = csv.DictWriter(output_file, fieldnames=keys)
    #         dict_writer.writeheader()
    #         dict_writer.writerows(jobs)

    # def save_jobs_to_dataframe(jobs, filename):
    #     df = pd.DataFrame(jobs)
    #     df.to_csv(filename, index=False, encoding='utf-8')
    #     print(df)




    # if __name__ == "__main__": 
    #     # ->main() 
    #     # import thisfile.py module: False because __name__==thisfile//running script:True __name__==__main__
    #     # 一旦导入模块就会执行文件中的顶级代码
    
    #     start_url = "https://www.zhipin.com/web/geek/job?query=%E8%BF%90%E8%90%A5&city=101020100&page=1"  # 替换为实际的起始URL
    #     all_jobs = scrape_all_jobs(start_url)
        # save_jobs_to_csv(all_jobs, "jobs.csv")
        # # save_jobs_to_dataframe(all_jobs, "jobs_dataframe.csv")
        # for job in all_jobs:
        #     print(job)
   
