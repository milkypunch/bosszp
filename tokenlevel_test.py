import requests

# 一级页面的 token
token = "40dafw5DDsMSPIkAcHFhtIsKOd8K6Y2NySsKlWnLCk2TDklzCjsOOWsK%2FaMOTwrbDjsKqwofDgMK9ccKiXEdjw5NzwpzCpMKewrrDgsKawqrCqsKRWsKbxJbEjsK%2Bw5TCr8KxwrrCskEpBAoeCgoGEBwQEB0jHgoKIx0RHR0QBiIGBkE%2BxI5awr03QEE6JF1jRwRIbFleWUQKV19FOkBWIwoQQDwhOjo0w43DuMK3w4PDk8O0w5PCvsONw7rCt8KKOlI0OsONw6EnOMOBwqgrbBDDgcKlK0wQOCLDimxoRlDCusOgKUBNwrtNNxRAQUFNQU1SQTckTR7DinJ%2BYlzCusOYMU4hOTdBNDdBN0E6QVMrQTZBKzc6Pk0HIiMiBzBSwrbCucK6w603QQ%3D%3D"

# 二级页面的 API 端点
url = "https://www.zhipin.com/wapi/zpgeek/search/joblist.json?scene=1&query=%E8%BF%90%E8%90%A5&city=101020100&experience=&payType=&partTime=&degree=&industry=&scale=&stage=&position=&jobType=&salary=&multiBusinessDistrict=&multiSubway=&page=6&pageSize=30"

# 请求头
headers = {
    "Authorization": f"Bearer {token}"
}

# 发送 GET 请求
response = requests.get(url, headers=headers)

# 处理响应
if response.status_code == 200:
    print("Access to second level resource successful:", response.json())
else:
    print("Failed to access second level resource:", response.status_code, response.text)