import requests

def make_request():
    session = requests.Session()
    response = session.get('https://www.zhipin.com/wapi/zpgeek/search/joblist.json?scene=1&query=%E8%BF%90%E8%90%A5&city=101020100&experience=&payType=&partTime=&degree=&industry=&scale=&stage=&position=&jobType=&salary=&multiBusinessDistrict=&multiSubway=&page=1&pageSize=30')
    
    print(response.json())
    cookies = session.cookies.get_dict()
    print(cookies)
    session.close()

for _ in range(10):
    make_request()
