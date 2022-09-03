import os
from fastapi import FastAPI, Request, Response, Header, HTTPException
from fastapi.encoders import jsonable_encoder
import hashlib
import hmac
import http
import requests
import json
import toml

# 读取配置文件
toml_config_path = os.path.join(os.path.dirname(__file__), "config.toml")
config = toml.load(toml_config_path)

wechat_bot_webhook_link = config['wechat_bot_webhook_link']
WEBHOOK_SECRET = config['WEBHOOK_SECRET']
env = config['env']

# 根据环境变量判断是否开启 api 文档
if env != 'dev':
    app = FastAPI(docs_url=None, redoc_url=None)
else:
    app = FastAPI()


# 创建 hash 签名
def generate_hash_signature(
    secret: bytes,
    pyload: bytes,
    digest_method=hashlib.sha1,
):
  return hmac.new(secret, pyload, digest_method).hexdigest()

@app.post("/webhook", status_code=http.HTTPStatus.ACCEPTED)
async def webhook(request: Request, x_hub_signature:str = Header(None)):
    """webhook 中转服务  
    :param request: 来自 Github Repo 的请求  
    :param x_hub_signature: Github Repo 请求头中的签名
    """
    # 计算签名
    pyload = await request.body()
    secret = WEBHOOK_SECRET.encode("utf-8")
    signature = generate_hash_signature(secret, pyload)
    # 验证签名
    if x_hub_signature != f"sha1={signature}":
        raise HTTPException(status_code=403, detail="Forbidden")
    # 获取请求体并转换为 json(dict)
    data = jsonable_encoder(pyload.decode("utf-8"))
    data = json.loads(data)
    # 仓库及分支
    repo_head = data['repository']['name'] + ':' + data['ref'].split('/')[-1]
    # 仓库链接
    repo_link = data['repository']['url']
    # 提交作者
    author = data['commits'][0]['author']['name']
    # 提交信息
    commit_message = data['commits'][0]['message']
    # 提交链接
    commit_link = data['commits'][0]['url']
    
    # 推送 markdown 信息
    post_markdown = "[{0}]({1}) 1 new commit by {2} \n\n [{3}]({4})"\
        .format(repo_head, repo_link, author, commit_message, commit_link)
    
    # 调用企微 Bot Webhook 接口推送消息
    requests.post(
        url=wechat_bot_webhook_link,
        headers={
        "Content-Type": "application/json",
        },
        json={
            "msgtype": "markdown",
            "markdown": {
                "content": post_markdown
                },
        },
    )

    return {}


if __name__ == "__main__":
    # 获取配置文件中的 uvicorn 启动参数并启动服务
    os.system("uvicorn main:app" + " " \
        + config['uvicorn']['reload'] + " " \
            + "--host " + config['uvicorn']['host'] + " " \
                + "--port " + str(config['uvicorn']['port']))
