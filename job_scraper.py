import requests
import random
import time
from fake_useragent import UserAgent

class JobScraper:
    def __init__(self, cookie_manager):
        self.base_url='https://www.zhipin.com/wapi/zpgeek/search/joblist.json?scene=1&query=%E8%BF%90%E8%90%A5&city=101020100&experience=&payType=&partTime=&degree=&industry=&scale=&stage=&position=&jobType=&salary=&multiBusinessDistrict=&multiSubway='
        self.start_url = 'https://www.zhipin.com/wapi/zpgeek/search/joblist.json?scene=1&query=%E8%BF%90%E8%90%A5&city=101020100&experience=&payType=&partTime=&degree=&industry=&scale=&stage=&position=&jobType=&salary=&multiBusinessDistrict=&multiSubway=&page=1&pageSize=30'
        self.proxy = 'http://127.0.0.1:7890'
        self.ua = UserAgent()
        self.cookie_manager = cookie_manager

    # def create_session(self):
    #     session = requests.Session()
    #     session.headers.update({
    #         'User-Agent': self.ua.random,
    #         'Accept': 'application/json, text/plain, */*',
    #         'Connection': 'keep-alive'
    #     })
    #     if self.proxy:
    #         session.proxies.update({
    #             'http': self.proxy,
    #             'https': self.proxy
    #         })
    #     return session

    def request_page(self, url, retries=3, timeout=60):
        while retries > 0:
            session = self.create_session()
            cookies = self.cookie_manager.get_random_cookie() if self.cookie_manager else []

            # 添加 Cookie 到会话
            for cookie in cookies:
                session.cookies.set(cookie['name'], cookie['value'])

            try:
                response = session.get(url, timeout=timeout)
                response.raise_for_status()  # 检查请求是否成功
                return response.json()
            except (requests.exceptions.RequestException, Exception) as e:
                print(f"发生错误: {e}")
                retries -= 1
                print(f"重试剩余次数: {retries}")
                
                # 刷新 token
                # self.cookie_manager.refresh_token()
                
                # 随机等待5到10秒后重试
                time.sleep(random.uniform(5, 10))
                
            finally:
                # 确保无痕
                session.cookies.clear()
        
        print("页面加载失败")
        return None

    def scrape_jobs(self):
        all_jobs = []
        page = 1
        has_more = True

        while has_more:
            url = f"{self.base_url}&page={page}&pageSize=30"  # 构造分页 URL
            data = self.request_page(url)
            if data:
                zp_data = data.get('zpData', {})
                job_list = zp_data.get('jobList', [])
                all_jobs.extend(job_list)
                
                # 直接获取 hasMore 值
                has_more = zp_data.get('hasMore', False)
                page += 1
            else:
                print(f"获取第 {page} 页数据失败")
                break

        return all_jobs
        # list of job_list(/page)


    def parse_job_list(self, all_jobs):
        parsed_jobs = []
        for job_list in all_jobs:
            for item in job_list:
                parsed_jobs.append({
                    "job_name": item.get("jobName", ""),
                    "job_area": item.get("areaDistrict", ""),
                    "salary": item.get("salaryDesc", ""),
                    "job_degree": item.get("jobDegree", ""),
                    "job_experience": item.get("jobExperience", ""),
                    "days_per_week": item.get("daysPerWeekDesc", ""),
                    "least_month": item.get("leastMonthDesc", ""),
                    "cpn_name": item.get("brandName", ""),
                    "cpn_type": item.get("brandIndustry", ""),
                    "finance_stage": item.get("brandStageName", ""),
                    "cpn_scale": item.get("brandScaleName", ""),
                    "welfare": item.get("welfareList", [])
                })
        return parsed_jobs
# request_page和parse detail嵌套
        # for url in urls:
        # request_page(url)
        # 把return response.json()改成response.text
        # soup = BeautifulSoup(r, 'html.parser')
        #         job_desc_div = soup.find("div", class_="job-sec-text")
        #         if job_desc_div:
        #             job_desc = job_desc_div.get_text(separator="\n").strip()
        # get_text是什么方法
                    # return job_desc