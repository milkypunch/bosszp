

# 假设已知sms_text, 提取六位验证码
import re

def extract_code_from_sms(sms_text):
    # 使用正则表达式匹配六位数字验证码
    match = re.search(r'\b\d{6}\b', sms_text)
    if match:
        return match.group(0)
    return None

# 示例短信内容
sms_text = "您的验证码是：123456，请在5分钟内使用。"
code = extract_code_from_sms(sms_text)
print(f"提取的验证码是: {code}")

# 发送给bark
import os
import json
def send_code_to_bark(code):
    bark_key = "A97w9GykfSLoxJCZqsom3B/"  # 替换为你的 Bark 推送 key
    bark_url = f"https://api.day.app/{bark_key}"
    payload = {
        "body": f"验证码：{code}",
        "title": "验证码推送"
    }
    command = f"curl -X POST {bark_url} -H 'Content-Type: application/json; charset=utf-8' -d '{json.dumps(payload)}'"
    os.system(command)

# 发送提取的验证码
send_code_to_bark(code)


# 推送到服务器
from fastapi import FastAPI, Request
from pydantic import BaseModel
import uvicorn

app = FastAPI()

class CodeRequest(BaseModel):
    body: str

@app.post("/receive_code")
async def receive_code(request: CodeRequest):
    code = request.body
    # 将验证码写入爬虫代码或存储到数据库
    save_code_to_db(code)
    return {"status": "success"}

def save_code_to_db(code: str):
    # 实现保存验证码到数据库的逻辑
    print(f"Received code: {code}")


