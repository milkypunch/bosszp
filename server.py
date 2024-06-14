from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI()

class CodeRequest(BaseModel):
    # 用于解析请求体的数据模型
    # 自动将请求体解析为 CodeRequest 类型的实例 
    # -> 在处理请求的函数中直接使用这个实例，而不需要手动解析 JSON 数据
    body: str
    # 定义请求体中要提取的部分的数据类型
    # pydantic 会自动验证请求体的数据类型是否符合定义

latest_code = None


# 路径（或路由）：客户端用来访问特定资源或执行特定操作的 URL
# 定义客户端与服务器如何进行交互
# app.post: 定义处理post请求，关联函数+请求方法+路径   
@app.post("/receive_code")
async def receive_code(request: CodeRequest):
    # 处理向该路径发送的请求的异步函数（不阻塞主线程）
    # 请求体会被处理为实例:request
    global latest_code
    message = request.body
    # 提取验证码
    import re
    match = re.search(r'验证码：(\d{6})', message)
    if match:
        latest_code = match.group(1)
    save_message_to_db(latest_code)
    return {"status": "success"} # 怎样在手机上看到

@app.get("/get_latest_code")
async def get_latest_code():
    global latest_code
    if latest_code:
        return {"code": latest_code}
    else:
        return {"code": None}
# 这个函数的作用是提供一个接口，允许客户端获取最新的验证码。
# 因为它可以通过这个接口来获取最新的验证码，而不需要直接访问服务器的内部状态。


def save_message_to_db(message: str):
    print(f"Received message: {message}")

def run_server():
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    run_server()
