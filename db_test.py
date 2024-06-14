import requests # 导入网页请求库
from bs4 import BeautifulSoup # 导入网页解析库
import json # 用于将列表字典（json格式）转化为相同形式字符串，以便存入文件


def start_requests(url):
    headers={'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'}

    r = requests.get(url,headers=headers)
    print(r.status_code)
    return r.content

def parse(text):
    soup = BeautifulSoup(text, 'html.parser')
    movie_list = soup.find_all('div', class_ = 'item')
    for movie in movie_list:
        mydict = {}
        mydict['title'] = movie.find('span', class_ = 'title').text
        mydict['score'] = movie.find('span', class_ = 'rating_num').text
        quote = movie.find('span', class_ = 'inq')
        mydict['quote'] = quote.text if quote else None
        star = movie.find('div', class_ = 'star')
        mydict['comment_num'] = star.find_all('span')[-1].text[:-3]
        yield mydict # 这里使用生成器

def get_all(): # 获取所有页封装成一个函数
    for i in range(2):
        url = 'https://movie.douban.com/top250?start={}&filter='.format(i * 25)
        text = start_requests(url)
        result = parse(text)
        
        yield from result # 返回一个生成器


s=list(get_all())
j=json.dumps(s,indent=4,ensure_ascii=False)
print(j)
with open('moviedb.json','w',encoding='utf-8') as f:
    f.write(j)


import psycopg2
from psycopg2 import sql

with open('moviedb.json','r') as f:
    content=f.read()

content=json.loads(content)



db_params={
    'dbname':'milkypunch',
    'user':'huihui',
    'password':'314159',
    'host':'localhost',
    'port':5432
}


try:
    conn=psycopg2.connect(**db_params)
    cur=conn.cursor()
    query="""
    CREATE TABLE IF NOT EXISTS public.movies (
        id SERIAL PRIMARY KEY,
        title VARCHAR(100),
        score NUMERIC(3,1),
        quote VARCHAR(100),
        comment_num INTEGER
    )
    """
    cur.execute(query)
    conn.commit()
    # alter_table_query = """
    # ALTER TABLE public.movies
    # ALTER COLUMN score TYPE VARCHAR(20),
    # ALTER COLUMN comment_num TYPE VARCHAR(20);
    # """
    # cur.execute(alter_table_query)
    # conn.commit()
    # print("列的数据类型修改成功")

    insert_query="""
    INSERT INTO public.movies (title, score, quote, comment_num)
    VALUES (%s, %s, %s, %s)
    """
    for dict in content:
        title = dict['title']
        score = float(dict['score'])
        quote = dict['quote']
        comment_num = int(dict['comment_num'])
    
        cur.execute(insert_query,(title, score, quote, comment_num))
    conn.commit()
    cur.close()
    conn.close()
except Exception as error:
    print(f"发生错误: {error}")