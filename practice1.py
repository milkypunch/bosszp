import requests # 导入网页请求库
from bs4 import BeautifulSoup # 导入网页解析库
import json

class newclass(object):
    def __init__(self):
        self.baseurl = 'https://movie.douban.com/top250'
        self.result_list=[]

    def start_requests(self,url):
        header={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'}
        r = requests.get(url, headers=header)
        
        return r.content

    def parse(self,text):
        soup = BeautifulSoup(text, 'html.parser')
        movie_list = soup.find_all('div', class_ = 'item')
        for movie in movie_list:
            mydict = {}
            mydict['title'] = movie.find('span', class_ = 'title').text
            mydict['score'] = movie.find('span', class_ = 'rating_num').text
            quote = movie.find('span', class_ = 'inq')
            mydict['quote'] = quote.text if quote else None # 抓取10页就总会遇到这种特殊情况要处理
            star = movie.find('div', class_ = 'star')
            mydict['comment_num'] = star.find_all('span')[-1].text[:-3]
            self.result_list.append(mydict) # 向全局变量result_list中加入元素
        nextpage = soup.find('span', class_ = 'next').a # 找到“下一页”位置
        if nextpage:# 找到的就再解析，没找到说明是最后一页，递归函数parse就运行结束 
            nexturl = self.baseurl + nextpage['href']
            text = self.start_requests(nexturl) # 多次使用这个函数，可以看出定义函数的好处，当请求更复杂的时候好处更明显 
            self.parse(text)

    def write_json(self,result):
        s = json.dumps(result, indent = 4, ensure_ascii=False)
        with open('movies.json', 'w', encoding = 'utf-8') as f:
            f.write(s)

    def start(self):
        text = self.start_requests(self.baseurl)
        self.parse(text)
        self.write_json(self.result_list) # 所有电影都存进去之后一起输出到文件

mv=newclass()
mv.start()