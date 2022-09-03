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


def generate_hash_signature(
    secret: bytes,
    pyload: bytes,
    digest_method=hashlib.sha1,
)-> str:
    """生成 HMAC 摘要  
    :param secret: 密钥
    :param pyload: 要加密的数据
    """
    return hmac.new(secret, pyload, digest_method).hexdigest()


def push_event(data: dict) -> str:
    """通过 data 获取 push 信息并生成相应 markdown 推送文本  
    :param data: push 事件中的 json data
    """
    # 仓库及分支
    repo_head = data['repository']['name'] + ':' + data['ref'].split('/')[-1]
    # 仓库链接
    repo_link = data['repository']['url']
    # 提交作者
    author = data['commits'][0]['author']['name']
    # 提交数量
    commit_count = len(data['commits'])
    if commit_count == 1:
        commit_count_markdown = '1 commit'
    else:
        commit_count_markdown = str(commit_count) + ' commits'

    commit_markdown = ''
    # 提交信息及链接(markdown)
    for commit in data['commits']:
        commit_markdown += '> [' + commit['message'] + '](' + commit['url'] + ')\n'

    post_markdown = f"[{repo_head}]({repo_link}) {commit_count_markdown}  by {author}:\n\n{commit_markdown}"

    return post_markdown


def ping_event(data: dict) -> str:
    """通过 data 获取 ping 信息并生成相应 markdown 推送文本  
    :param data: ping 事件中的 json data
    """
    # 仓库及分支
    repo_head = data['repository']['name']
    # 仓库链接
    repo_link = data['repository']['url']
    # 提交作者
    author = data['sender']['login']

    # author_avatar (目前企业微信还不支持 markdown 中的图片语法)
    # author_avatar = data['sender']['avatar_url']
    # author_avatar_markdown = f"![avatar]({author_avatar})"
    # post_markdown = f"[{repo_head}]({repo_link}) pinged by {author} {author_avatar_markdown}"

    post_markdown = f"[{repo_head}]({repo_link}) pinged by {author}"

    return post_markdown


def branch_or_tag_create_event(data: dict) -> str:
    """通过 data 获取 branch or tag create 信息并生成相应 markdown 推送文本  
    :param data: branch or tag create 事件中的 json data
    """
    # 仓库及分支
    repo_head = data['repository']['name'] + ':' + data['ref'].split('/')[-1]
    # 仓库链接
    repo_link = data['repository']['url']
    # 提交作者
    author = data['sender']['login']

    post_markdown = f"[{repo_head}]({repo_link}) branch/tag created by {author}"

    return post_markdown

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
    # 验证签名(不使用等式判断，使用 hmac.compare_digest 防止时序攻击)
    if not hmac.compare_digest(f"sha1={signature}", x_hub_signature):
        raise HTTPException(status_code=403, detail="Forbidden")
    # 获取请求体并转换为 json(dict)
    data = jsonable_encoder(pyload.decode("utf-8"))
    data = json.loads(data)

    # 获取 event 类型
    event = request.headers['X-GitHub-Event']
    print(event)

    # 处理 push 事件
    if event == 'push':
        post_markdown = push_event(data)
    # 处理 branch or tag create 事件
    elif event == 'create':
        post_markdown = branch_or_tag_create_event(data)
    # 处理 Webhook 初始化 ping 事件
    elif event == 'ping':
        post_markdown = ping_event(data)
    else:
        post_markdown = f"未处理事件: {event}"
    
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


