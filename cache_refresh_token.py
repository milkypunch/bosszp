#如何缓存token并在过期时重新获取：

import requests
import time

# 全局变量缓存token和过期时间
cached_token = None
token_expiry = 0

def get_token():
    global cached_token, token_expiry
    if cached_token is None or time.time() > token_expiry:
        # 登录获取新的token
        login_url = "https://example.com/api/login"
        login_data = {
            "username": "your_username",
            "password": "your_password"
        }
        response = requests.post(login_url, data=login_data)
        data = response.json()
        cached_token = data.get("token")
        token_expiry = time.time() + data.get("expires_in", 3600)  # 假设token有效期为1小时
    return cached_token

def access_secure_api():
    token = get_token()
    api_url = "https://example.com/api/secure-endpoint"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(api_url, headers=headers)
    return response.json()

# 使用示例
print(access_secure_api())