import scrapy
import logging
import random
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC




class BossSpider(scrapy.Spider):
    name = "boss"
    allowed_domains = ["zhipin.com"]
    start_urls = ["https://www.zhipin.com/web/geek/job?query=%E8%BF%90%E8%90%A5&city=101020100"]
    user_agents = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Safari/605.1.15',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0',
        'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
        'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
    ]
    cookies_list = [
    {'historyState':'state'},
    {'__l':'l=%2Fwww.zhipin.com%2Fweb%2Fgeek%2Fjob%3Fquery%3D%25E8%25BF%2590%25E8%2590%25A5%26city%3D101020100&r=&g=&s=3&friend_source=0'},
    {'wd_guid':'f28652e7-fb5e-4edb-9500-7e6bfd15d38b'},
    {'__a':'98585764.1715687087..1715687087.6.1.6.6'}
    ]
    #a dict/dicts?
    page_no = 1

    def random_headers(self):
        headers={"Referer":"https://www.zhipin.com/c101020100/?ka=sel-city-101020100"}
        headers['User-Agent']=random.choice(self.user_agents)
        return headers
    
    def random_cookies(self):
        return random.choice(self.cookies_list)


         
    def start_requests(self):
        url = 'https://www.zhipin.com/web/geek/job?query=%E8%BF%90%E8%90%A5&city=101020100&page=1'
        logging.info(f"<<<<<<<<<<<<<正在爬取第_{self.page_no}_页岗位数据>>>>>>>>>>>>>")

        yield SeleniumRequest(
    url=url,
    headers=self.random_headers(),
    cookies=self.random_cookies(),
    callback=self.parse,
    wait_time=10,
    wait_until=EC.presence_of_element_located((By.XPATH, '//ul[@class="job-list-box"]/li'))
)

#why not combine with parse
        
    def parse(self, response):
        if response.status != 200:
            logging.warning("<<<<<<<<<<<<<获取城市招聘信息失败，ip已被封禁。请稍后重试>>>>>>>>>>>>>")
            return
        
        self.log(f"Page content: {response.text()}")

        li_elements = response.xpath('//ul[@class="job-list-box"]/li')  

        if not li_elements:
            self.log("No job listings found. Please check the XPath expression.")
            return

        for li in li_elements:
            job_name = li.xpath('.//span[@class="job-name"]/text()').get()
            job_area = li.xpath('.//span[@class="job-area"]/text()').get()
            job_salary = li.xpath('.//span[@class="salary"]/text()').get()
            com_name = li.xpath('.//h3[@class="company-name"]/a/text()').get()
            com_type = li.xpath('.//ul[@class="company-tag-list"]/li[1]/text()').get()
            com_size = li.xpath('.//ul[@class="company-tag-list"]/li[3]/text()').get()
            finance_stage = li.xpath('.//ul[@class="company-tag-list"]/li[2]/text()').get()
            work_year = li.xpath('.//div[@class="job-info clearfix"]/ul[@class="tag-list"]/li[1]/text()').get()
            education = li.xpath('.//div[@class="job-info clearfix"]/ul[@class="tag-list"]/li[2]/text()').get()
            job_benefits = li.xpath('.//div[2]//div[@class="info-desc"]/text()').get()
            work_kws = li.xpath('./div[2]/li/text()')

            link=li.xpath('.//a[1]/@href').get()
            absolute_url=response.urljoin(link)  
            yield scrapy.Request(url=absolute_url,headers=self.random_headers(),cookies=self.random_cookies(),callback=self.parse_detail,meta={'item':item})








            item = BosszpItem(job_name=job_name, job_area=job_area, job_salary=job_salary, com_name=com_name,
                              com_type=com_type, com_size=com_size,
                              finance_stage=finance_stage, work_year=work_year, education=education,
                              job_benefits=job_benefits, work_kws=work_kws, job_desc=job_desc)
            yield item
        
        self.page_no += 1
        
        next_page = response.xpath(f'//a[text="{self.page_no}"]/@href').get() 
        disabled_next_page = response.xpath('//a[@class="disabled"]') 
        # check disabled existence
        # 2-10;false
        # page_no=11;true

        if next_page and not disabled_next_page:
            next_page_url = response.urljoin(next_page)
            logging.info(f"<<<<<<<<<<<<<正在爬取第_{self.page_no}_页岗位数据>>>>>>>>>>>>>") 
            yield SeleniumRequest(url=next_page_url, headers=self.random_headers(),cookies=self.random_cookies(),callback=self.parse)
        
        else:
            logging.info('<<<<<<<<<<<<<岗位数据已爬取结束>>>>>>>>>>>>>')
            logging.info(f"<<<<<<<<<<<<<一共爬取了_{self.page_no-1}_页岗位数据>>>>>>>>>>>>>")
            return
    
    
    def parse_detail(self,response):
        item=response.meta['item']
        job_desc=response.xpath('//div[@class="job-sec-text"]/text()').get()
        item['job_desc']=job_desc
        yield item



#def parse(self, response):
#       driver = response.meta['driver']
#       for page in range(1, 11):  # 爬取前10页
#           # 模拟点击分页链接
#           pagination_link = driver.find_element_by_xpath(f'//a[text()="{page}"]')
#           pagination_link.click()
#           
#           # 等待页面加载完成
#           WebDriverWait(driver, 10).until(
#               EC.presence_of_element_located((By.CSS_SELECTOR, '.content'))  # 修改为实际内容的选择器
#           )
#           
#           # 获取页面内容
#           page_source = driver.page_source
#           response = scrapy.http.HtmlResponse(url=driver.current_url, body=page_source, encoding='utf-8')
#           
#           # 处理页面内容
#           self.parse_page(response)