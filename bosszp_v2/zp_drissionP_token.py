import requests
import json
from typing import List, Dict
import time
import random
from bs4 import BeautifulSoup
import redis
import psycopg2
from requests.exceptions import SSLError
import hashlib
from DrissionPage import ChromiumOptions, WebPage


class JobCrawler:
    def __init__(self, base_url: str, params: Dict[str, str], referer: str):
        self.base_url = base_url
        self.params = params
        self.referer = referer
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,fr;q=0.8,en;q=0.7,zh-TW;q=0.6',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            # 'Cookie': 'ab_guid=651f07d9-4e58-497e-8a7d-4812c89f7277; __g=-; Hm_lvt_194df3105ad7148dcf2b98a91b5e727a=1736999191; HMACCOUNT=7A64FAD03A38812F; lastCity=101020100; wt2=DThyBL_b9nD3vb34M_Y6kCzAiuH2fJeGs526Mtdnosk2_Ij-JI6jiY2X2POpH6hac8L474dIgQrCoSIQNuyo54w~~; wbg=0; zp_at=zvn4C8pxN0boAWvCcD4tkFseY6_j7mWWN2_ehEOts2Q~; __l=l=%2Fwww.zhipin.com%2Fweb%2Fgeek%2Fjob-recommend%3Fcity%3D101020100%26salary%3D404%26degree%3D203&r=&g=&s=3&friend_source=0&s=3&friend_source=0; __c=1737109779; __a=86610528.1737109779..1737109779.84.1.84.84; Hm_lpvt_194df3105ad7148dcf2b98a91b5e727a=1737358931; bst=V2R9sgFub6319sVtRuzBUcKi207DrezS8~|R9sgFub6319sVtRuzBUcKi207DrfxSs~; __zp_stoken__=5618fSE3DosK1w4%2FDiUokGBgYHgRMJjVNORdPSDFBSEJITTNKQEhNSyg2OMO5wrVkSMKjV8OawqjCtjcyM0hOSE1BSDdLIjNMwrVITj7Ej8OJZE7CuG7DhhnCrcOKGXcZHQbCgMK3GSvCsyQ5wo7Di0o1TjXChMK1w7PDi8K7w4vEiMOMdcOKxILDjzU2NcOBMEkHB2oESTZEX1UDRGBQa21QA0dRXiQ1STRIw4TCtSM1BxgHHgQYBxgdAwcYBxkfGxwbGhAYBxgdAzA3wqzDgMOIw4piw7fDscSUwpbDj8SOR8O5wpPCokbDtcKjw4hDwpvCtsKGw4pebVBGwqnCpcOPwrXCrcONw43DgsKiUcOBwoxhasKkd8K5f3JDw4F%2BwopoEBEdHQc2HcOrxIHDmg%3D%3D',
            'Pragma': 'no-cache',
            'Referer': self.referer,
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            
        }
        self.cookies = {
            'wt2': 'DThyBL_b9nD3vb34M_Y6kCzAiuH2fJeGs526Mtdnosk2_Ij-JI6jiY2X2POpH6hac8L474dIgQrCoSIQNuyo54w~~',
            
        }
        self.r = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.conn = psycopg2.connect(
            dbname='milkypunch',
            user='huihui',
            password='314159',
            host='localhost',
            port=5432
        )
        self.create_jobs_table()

    def __del__(self):
        """确保关闭数据库连接"""
        if self.conn:
            self.conn.close()

    def create_jobs_table(self) -> None:
        """创建 jobs 表"""
        cur = self.conn.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS public.SH_5_10k_bac (
            job_id VARCHAR(50) PRIMARY KEY,
            district TEXT,
            job_name VARCHAR(100),
            salary VARCHAR(50),
            job_degree VARCHAR(50),
            job_experience VARCHAR(50),
            days_per_week VARCHAR(50),
            least_month VARCHAR(50),
            brand_name VARCHAR(100),
            brand_industry VARCHAR(100),
            brand_stage VARCHAR(100),
            brand_scale VARCHAR(100),
            welfare TEXT[],
            job_description TEXT,
            detail_url TEXT
        )
        """
        cur.execute(create_table_query)
        self.conn.commit()
        cur.close()

    @staticmethod
    def get_md5(job: Dict[str, str]) -> str:
        """
        生成 job 的 MD5 散列值作为唯一标识

        :param job: 工作信息字典
        :return: MD5 散列值
        """
        return hashlib.md5(str(job).encode('utf-8')).hexdigest()

    def check_duplication(self, job: Dict[str, str]) -> None:
        """
        数据去重后存入数据库

        :param job: 工作信息字典
        """
        hash_value = self.get_md5(job)
        result = self.r.sadd("zp_jobInfo", hash_value)
        
        # 只有在 Redis 中没有重复时才保存到数据库
        if result:
            self.save_jobs_in_db(job)
        else:
            print("数据重复")
    
    def save_jobs_in_db(self, job: Dict[str, str]) -> None:
        """
        存储单个 job 到数据库

        :param job: 工作信息字典
        """
        cur = self.conn.cursor()
        insert_query = """
        INSERT INTO public.SH_5_10k_bac (job_id, district, job_name, salary, job_degree, job_experience,
                                          days_per_week, least_month, brand_name, brand_industry,
                                          brand_stage, brand_scale, welfare, job_description, detail_url)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (job_id) DO UPDATE SET
            job_name = EXCLUDED.job_name,
            district = EXCLUDED.district,
            salary = EXCLUDED.salary,
            job_degree = EXCLUDED.job_degree,
            job_experience = EXCLUDED.job_experience,
            days_per_week = EXCLUDED.days_per_week,
            least_month = EXCLUDED.least_month,
            brand_name = EXCLUDED.brand_name,
            brand_industry = EXCLUDED.brand_industry,
            brand_stage = EXCLUDED.brand_stage,
            brand_scale = EXCLUDED.brand_scale,
            welfare = EXCLUDED.welfare, 
            job_description = EXCLUDED.job_description,
            detail_url = EXCLUDED.detail_url
        """
        try:
            cur.execute(insert_query, (
                job.get("job_id"),
                job.get("district"),
                job.get("job_name"),
                job.get("salary"),
                job.get("job_degree"),
                job.get("job_experience"),
                job.get("days_per_week"),
                job.get("least_month"),
                job.get("brand_name"),
                job.get("brand_industry"),
                job.get("brand_stage"),
                job.get("brand_scale"),
                job.get("welfare"),
                job.get("job_description"),
                job.get("detail_url")
            ))
            self.conn.commit()
            cur.close()
            print("Jobs inserted in the database successfully.")
        except Exception as error:
            print(f"Error inserting jobs in the database: {error}")

    def parse_jobs(self, data: dict) -> List[Dict[str, str]]:
        """
        解析职位数据并返回职位列表

        :param data: 请求网站响应的 JSON 数据
        :return: 职位信息字典列表
        """
        jobs_on_page = []
        
        if data:
            zp_data = data.get('zpData', {})
            lid = zp_data.get('lid')
            job_list = zp_data.get('jobList', [])

            print(f'get {len(job_list)} jobs from page')
            
            for item in job_list:
                encryptJobId = item.get("encryptJobId", "")
                securityId = item.get("securityId", "")

                jobs_on_page.append({
                    "lid": lid,
                    "job_id": encryptJobId,
                    "securityId": securityId,
                    "district": ('·').join([item.get("areaDistrict", ""),item.get("businessDistrict","")]),
                    "job_name": item.get("jobName", ""),
                    "salary": item.get("salaryDesc", ""),
                    "job_degree": item.get("jobDegree", ""),
                    "job_experience": item.get("jobExperience", ""),
                    "days_per_week": item.get("daysPerWeekDesc", ""),
                    "least_month": item.get("leastMonthDesc", ""),
                    "brand_name": item.get("brandName", ""),
                    "brand_industry": item.get("brandIndustry", ""),
                    "brand_stage": item.get("brandStageName", ""),
                    "brand_scale": item.get("brandScaleName", ""),
                    "welfare": item.get("welfareList", []),
                    
                })
        else:
            print("数据解析失败")

        # print(jobs_on_page[0])
        return jobs_on_page

    def update_token(self) -> None:
        """更新 zpstoken"""
        co = ChromiumOptions().auto_port()
        co.incognito()
        # co.headless(False) 不能设置无头 需要看到是否封IP

        page = WebPage(chromium_options=co)
        page.get('https://www.zhipin.com/web/geek/job?query=Java&city=101020100')
        
        page.wait.eles_loaded('.job-list-wrapper')
        time.sleep(5)
        for cookie in page.cookies():
            if cookie['name'] == '__zp_stoken__':
                # 存储 token 和使用计数到 Redis
                token_info = {
                    'token': cookie['value'],
                    'usage_count': 0  # 初始化使用次数
                }
                self.r.set('__zp_stoken__', json.dumps(token_info))  # 将字典转为 JSON 字符串存储
                self.cookies['__zp_stoken__'] = cookie['value']
       
        page.quit()

    def use_token(self) -> None:
        """使用 zpstoken，检查使用次数或是否存在并决定是否更新"""
        token_info = self.r.get('__zp_stoken__')
        
        # 确保token存在
        if token_info is None:
            print("zpstoken不存在，正在生成新的值...")
            self.update_token()  
            token_info = self.r.get('__zp_stoken__')  
        
        
        token_info = json.loads(token_info)

        # 检查使用次数
        if token_info['usage_count'] >= 6:
            print("使用次数超过 6 次，重新生成新的值...")
            self.update_token()  
            token_info = json.loads(self.r.get('__zp_stoken__'))  

        
        self.cookies['__zp_stoken__'] = token_info['token']
        
        # 增加使用计数并更新使用次数信息
        token_info['usage_count'] += 1
        self.r.set('__zp_stoken__', json.dumps(token_info))  

    def get_job_description(self, desc_url: str, params: Dict) -> str:
        """
        获取职位详情，根据响应格式进行异常处理

        :param desc_url: 职位详情页的 URL
        :param params: 查询参数字典
        :return: 职位详情文本
        """
        while True:
            try:
                self.use_token()
                response = requests.get(desc_url, headers=self.headers,
                                            params=params, cookies=self.cookies)
                response.raise_for_status()  
                content_type = response.headers.get('Content-Type', '')

                if 'application/json' in content_type:
                    # 处理 JSON 响应
                    try:
                        data = response.json()  
                        
                    except ValueError as e:
                        print("JSON 解码失败:", e)
                

                    if data.get("message") == "您的访问行为异常.":
                        print("message: 您的访问行为异常.")
                        self.update_token()
                        time.sleep(1) 
                        continue  

                    if data.get("message") == "您的 IP 存在异常访问行为，暂时被禁止访问！":
                        print('IP blocked')
                        time.sleep(10)
                        continue

                elif 'text/html' in content_type:
                    # 提取 HTML 内容
                    html_content = response.text
                    soup = BeautifulSoup(html_content, 'html.parser')
                    job_desc_div = soup.find("div", class_="job-sec-text")
                    if job_desc_div:
                        job_desc = job_desc_div.get_text(separator="\n").strip()
                        return job_desc
                    else:
                        print("Job description div not found")
                        return "Error or find no job description"
                        
                               
            except requests.RequestException as e:
                print(f"Error fetching job description: {e}")
                time.sleep(5)
                continue
            except Exception as e:
                print(f"Unexpected error: {e}")
                time.sleep(5)
                continue

    def enrich_jobs_with_links_and_descriptions(self, job: Dict[str, str]) -> Dict[str, str]:
        """
        补充职位信息，包括详情页文本内容和链接

        :param job: 职位信息字典
        :return: 添加了职位详情和链接的职位信息字典
        """

        job_id = job.get("job_id")
        lid = job.get("lid")
        securityId = job.get("securityId")
        desc_url = f'https://www.zhipin.com/job_detail/{job_id}.html'
        params = {
            'lid': lid,
            'securityId': securityId,
            'sessionId': '',
        }
        try:
            job_description = self.get_job_description(desc_url, params)
            # time.sleep(10)                                                                                                                                                                             
            job["job_description"] = job_description
            job["detail_url"] = f"https://www.zhipin.com/job_detail/{job_id}?lid={lid}&securityId={securityId}&sessionId="
            
            return job


        except Exception as e:
            print(f"Error enriching job {job_id} with description: {e}")

    def fetch_jobs(self) -> List[Dict[str, str]]:
        """
        抓取职位信息并返回职位列表

        :return: 包含所有职位信息的字典列表
        """
        page = 1
        
        has_more = True


        while has_more:

            self.params['page'] = str(page)
            self.use_token()
            try:

                response = requests.get(url=self.base_url, headers=self.headers, cookies = self.cookies, params=self.params)
            except SSLError as e:
                print(f"SSL error occurred: {e}. Pausing for a few seconds before retrying...")
                time.sleep(random.randint(3, 5))
                continue  

            except requests.exceptions.RequestException as e:
                print(f"Request failed: {e}")
                break  # 处理其他请求异常

            
            data = response.json()
            
            # 情况1: token过期
            if data["message"] == "您的访问行为异常.":
                print("message: 您的访问行为异常.")

                self.update_token()
                time.sleep(1) 
                continue  
            
            # 情况2: IP
            if data["message"] == "您的 IP 存在异常访问行为，暂时被禁止访问！" or data["message"] == "您的IP地址存在异常行为.":
                print('IP blocked')
                continue

            jobs = self.parse_jobs(data)

            
            for job in jobs:
                
                job = self.enrich_jobs_with_links_and_descriptions(job)    
                
                del job['lid']
                del job['securityId']
                print(job)
                
                self.check_duplication(job)
            # 检查是否有更多页面
            has_more = data.get("zpData", {}).get("hasMore", False)
            
            page += 1
            
            time.sleep(random.randint(3, 5))


if __name__ == "__main__":
    base_url = 'https://www.zhipin.com/wapi/zpgeek/search/joblist.json'  
    # 上海 5-10k 本科  
    params = {
    'scene': '1',
    'query': '',
    'city': '101020100',
    'experience': '',
    'payType': '',
    'partTime': '',
    'degree': '203', # 本科
    'industry': '',
    'scale': '',
    'stage': '',
    'position': '',
    'jobType': '',
    'salary': '404',
    'multiBusinessDistrict': '',
    'multiSubway': '',
    'page': '1',
    'pageSize': '30',
}
    referer = 'https://www.zhipin.com/web/geek/job?city=101020100&degree=203&salary=404'
    crawler = JobCrawler(base_url, params, referer)

    crawler.fetch_jobs()
