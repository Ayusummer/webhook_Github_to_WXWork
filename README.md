# webhook_Github_to_WXWork
Github Repo Webhook 推送到企微群的中转服务

# TODO

- [x] Push 事件
- [ ] Release 事件
- [ ] Wiki 事件
- [ ] Star 事件
- [ ] Watch 事件

---

# 部署说明

## 1. 在企业微信群添加机器人并获取 Webhook 地址

![image-20220903124847548](http://cdn.ayusummer233.top/img/202209031248713.png)

![image-20220903125400223](http://cdn.ayusummer233.top/img/202209031254340.png)

---

## 2. 开发环境准备

准备一台服务器  
> 有公网 ip 的机器即可, 有没有域名都行

安装 git, Python, [poetry ](https://github.com/Ayusummer/DailyNotes/blob/main/Language/Python/%E5%BC%80%E5%8F%91%E7%8E%AF%E5%A2%83.md#poetry) 并[编辑 poetry 配置文件配置在项目目录配置虚拟环境](https://github.com/Ayusummer/DailyNotes/blob/main/Language/Python/%E5%BC%80%E5%8F%91%E7%8E%AF%E5%A2%83.md#%E9%85%8D%E7%BD%AE%E6%96%87%E4%BB%B6)

> 或者使用 当前项目配置文件中的 Python 版本的 [conda](https://github.com/Ayusummer/DailyNotes/blob/main/Language/Python/%E5%BC%80%E5%8F%91%E7%8E%AF%E5%A2%83.md#anaconda) 或者其他虚拟环境均可


---

## 3. 部署服务

1. 拉取代码

```bash
git clone https://github.com/Ayusummer/webhook_Github_to_WXWork.git
```

2. 安装依赖

```bash
cd webhook_Github_to_WXWork
poetry install
```

3. 编辑 `config.toml` 文件

4. (Linux) 使用 screen 或者 tmux 或者 zellij 创建一个窗口

5. 启动服务

```bash
poetry run python main.py
```

6. (Linux) 挂起 screen/tmux/zellij 窗口

---

## 4. 配置 Github Webhook

1. 进入 Github 项目的 Settings -> Webhooks -> Add webhook
2. 填写相关配置
   - `Payload URL`: `http(s)://[你的域名或者ip]:[config.toml中的端口号]/webhook`
   - `Content type`: `application/json`
   - `Secret`: `你在 config.toml 中配置的 secret`
   - `Witch events would you like to trigger this webhook?`: `Let me select individual events -> Pushes`    
     > 或者直接选 everything 也是可以的, 只不过目前只写了 push 事件的逻辑 