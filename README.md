# webhook_Github_to_WXWork
Github Repo Webhook 推送到企微群的中转服务

# TODO

> 由于后续基本没太有相关需求, 因此暂时摸了, 后面有需要再继续写

- 更多事件支持
  - [x] Pushes
  - [x] Branch or tag creation
        > 处理了但没完全处理, 只是简单的把事件类型发出来了, 等见得多了再完善
  - [x] ping
  - [ ] Releases
  - [ ] Wiki
  - [ ] Stars
  - [ ] Watches
  - [ ] Branch or tag deletion
  - [ ] Branch protection rules
  - [ ] Check runs
  - [ ] Check suites
  - [ ] Code scanning alerts
  - [ ] Collaborator add, remove, or changed
  - [ ] Commit comments
  - [ ] Deploy keys
  - [ ] Deployment statuses
  - [ ] Deployments
  - [ ] Discussion comments
  - [ ] Discussions
  - [ ] Forks
  - [ ] Issue comments
  - [ ] Issues
  - [ ] Labels
  - [ ] Meta
  - [ ] Milestones
  - [ ] Packages
  - [ ] Page builds
  - [ ] Project cards
  - [ ] Project columns
  - [ ] Projects
  - [ ] Pull request review comments
  - [ ] Pull request review threads
  - [ ] Pull request reviews
  - [ ] Pull requests
  - [ ] Registry packages
  - [ ] Repositories
  - [ ] Repository imports
  - [ ] Repository vulnerability alerts
  - [ ] Secret scanning alert locations
  - [ ] Secret scanning alerts
  - [ ] Security and analyses
  - [ ] Statuses
  - [ ] Team adds
  - [ ] Visibility changes
  - [ ] Workflow jobs
  - [ ] Workflow runs

- 安全能力提升
  - [ ] 使用 HMAC-256 

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

3. 删除 `config.toml_tmp` 的 `_tmp` 或者复制一份 `config.toml` 并编辑 `config.toml` 文件

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

---
# 思路

` Github(Webhook) + Python(fastAPI, requests) + 企微 Bot(Webhook)`

> `PS`:  `Gitee` 仓库的 webhook 的推送格式和企微的接口是可以对应上的, 不需要额外再转换

由于 GitHub 仓库 webhook 推送格式和企微 Bot 的推送格式不同, 因此如果想要将 GitHub 仓库的变动推送到企业微信的话, 那么就需要在中间做一层转发, 将 GitHub Repo Webhook 的推送格式转换成企微 Bot(Webhook) 的推送格式

> Gitee, Github, Gitlab 仓库 Webhook 推送格式详见 [不同 Repo 的 Webhook 推送格式](#不同 Repo 的 Webhook 推送格式)

---

## 在服务器上部署中转服务

> [Creating webhooks - GitHub Docs](https://docs.github.com/en/developers/webhooks-and-events/webhooks/creating-webhooks)  
> [Securing your webhooks - GitHub Docs](https://docs.github.com/en/developers/webhooks-and-events/webhooks/securing-your-webhooks)  
> [Build a Webhook Endpoint with FastAPI | by ukyen | Towards Dev](https://towardsdev.com/build-a-webhook-endpoint-with-fastapi-d14bf1b1d55d)  
> [Webhook events and payloads - GitHub Docs](https://docs.github.com/cn/developers/webhooks-and-events/webhooks/webhook-events-and-payloads)  
> [一日一技：FastAPI如何关闭接口文档？ - 腾讯云开发者社区-腾讯云 (tencent.com)](https://cloud.tencent.com/developer/article/1697199)

这里使用 FastAPI 来写中转接口, 然后在接口中通过 requests 库将重新调整后的 json 通过调用企微 Bot Webhook 推送到企微群聊

---

# 附录

## 不同 Repo 的 Webhook 推送格式

---

### Gitee Repo Webhook

`Headers`:

```
Request URL: ***
Request Method: POST
X-Git-Oschina-Event: Push Hook
X-Gitee-Token: 
X-Gitee-Event: Push Hook
User-Agent: git-oschina-hook
X-Gitee-Timestamp: 1662168189458
X-Gitee-Ping: false
Content-Type: application/json
```

`Pyload`:

```json
{
  "hook_id": 1169482,
  "hook_name": "push_hooks",
  "hook_url": "https://gitee.com/ayusummer233/Test-QHQC/hooks/1169482/edit",
  "markdown": {
    "content": "[咸鱼型233](https://gitee.com/ayusummer233) 推送到了 [咸鱼型233/浅海轻唱轴测试](https://gitee.com/ayusummer233/Test-QHQC) 的 [master](https://gitee.com/ayusummer233/Test-QHQC/tree/master) 分支\n > [咸鱼型233](https://gitee.com/ayusummer233) - [d78785d](https://gitee.com/ayusummer233/Test-QHQC/commit/d78785d0e6c6cf40a12e4c1d53443a2544f10698) webhook 推送测试\n\nSigned-off-by..."
  },
  "msgtype": "markdown",
  "password": "",
  "sign": "",
  "timestamp": "1662168189458",
  "key": "***"
}
```



---

### Github Repo Webhook

`Headers`:

```
Request URL: ***
Request method: POST
Accept: */*
content-type: application/json
User-Agent: GitHub-Hookshot/***
X-GitHub-Delivery:***
X-GitHub-Event: push
X-GitHub-Hook-ID: ***
X-GitHub-Hook-Installation-Target-ID: ***
X-GitHub-Hook-Installation-Target-Type: repository
X-Hub-Signature: sha1=***
X-Hub-Signature-256: ***
```

`Pyload`:

```json
{
  "ref": "refs/heads/main",
  "before": "af5ffecce599c60ae769a74a957b052aedc0cbe9",
  "after": "da7a8f85a9030e062cdc3edbc2076b16666818a1",
  "repository": {
    "id": 331657268,
    "node_id": "MDEwOlJlcG9zaXRvcnkzMzE2NTcyNjg=",
    "name": "DailyNotes",
    "full_name": "Ayusummer/DailyNotes",
    "private": false,
    "owner": {
      "name": "Ayusummer",
      "email": "ayusummer233@qq.com",
      "login": "Ayusummer",
      "id": 59549826,
      "node_id": "MDQ6VXNlcjU5NTQ5ODI2",
      "avatar_url": "https://avatars.githubusercontent.com/u/59549826?v=4",
      "gravatar_id": "",
      "url": "https://api.github.com/users/Ayusummer",
      "html_url": "https://github.com/Ayusummer",
      "followers_url": "https://api.github.com/users/Ayusummer/followers",
      "following_url": "https://api.github.com/users/Ayusummer/following{/other_user}",
      "gists_url": "https://api.github.com/users/Ayusummer/gists{/gist_id}",
      "starred_url": "https://api.github.com/users/Ayusummer/starred{/owner}{/repo}",
      "subscriptions_url": "https://api.github.com/users/Ayusummer/subscriptions",
      "organizations_url": "https://api.github.com/users/Ayusummer/orgs",
      "repos_url": "https://api.github.com/users/Ayusummer/repos",
      "events_url": "https://api.github.com/users/Ayusummer/events{/privacy}",
      "received_events_url": "https://api.github.com/users/Ayusummer/received_events",
      "type": "User",
      "site_admin": false
    },
    "html_url": "https://github.com/Ayusummer/DailyNotes",
    "description": "日常学习记录",
    "fork": false,
    "url": "https://github.com/Ayusummer/DailyNotes",
    "forks_url": "https://api.github.com/repos/Ayusummer/DailyNotes/forks",
    "keys_url": "https://api.github.com/repos/Ayusummer/DailyNotes/keys{/key_id}",
    "collaborators_url": "https://api.github.com/repos/Ayusummer/DailyNotes/collaborators{/collaborator}",
    "teams_url": "https://api.github.com/repos/Ayusummer/DailyNotes/teams",
    "hooks_url": "https://api.github.com/repos/Ayusummer/DailyNotes/hooks",
    "issue_events_url": "https://api.github.com/repos/Ayusummer/DailyNotes/issues/events{/number}",
    "events_url": "https://api.github.com/repos/Ayusummer/DailyNotes/events",
    "assignees_url": "https://api.github.com/repos/Ayusummer/DailyNotes/assignees{/user}",
    "branches_url": "https://api.github.com/repos/Ayusummer/DailyNotes/branches{/branch}",
    "tags_url": "https://api.github.com/repos/Ayusummer/DailyNotes/tags",
    "blobs_url": "https://api.github.com/repos/Ayusummer/DailyNotes/git/blobs{/sha}",
    "git_tags_url": "https://api.github.com/repos/Ayusummer/DailyNotes/git/tags{/sha}",
    "git_refs_url": "https://api.github.com/repos/Ayusummer/DailyNotes/git/refs{/sha}",
    "trees_url": "https://api.github.com/repos/Ayusummer/DailyNotes/git/trees{/sha}",
    "statuses_url": "https://api.github.com/repos/Ayusummer/DailyNotes/statuses/{sha}",
    "languages_url": "https://api.github.com/repos/Ayusummer/DailyNotes/languages",
    "stargazers_url": "https://api.github.com/repos/Ayusummer/DailyNotes/stargazers",
    "contributors_url": "https://api.github.com/repos/Ayusummer/DailyNotes/contributors",
    "subscribers_url": "https://api.github.com/repos/Ayusummer/DailyNotes/subscribers",
    "subscription_url": "https://api.github.com/repos/Ayusummer/DailyNotes/subscription",
    "commits_url": "https://api.github.com/repos/Ayusummer/DailyNotes/commits{/sha}",
    "git_commits_url": "https://api.github.com/repos/Ayusummer/DailyNotes/git/commits{/sha}",
    "comments_url": "https://api.github.com/repos/Ayusummer/DailyNotes/comments{/number}",
    "issue_comment_url": "https://api.github.com/repos/Ayusummer/DailyNotes/issues/comments{/number}",
    "contents_url": "https://api.github.com/repos/Ayusummer/DailyNotes/contents/{+path}",
    "compare_url": "https://api.github.com/repos/Ayusummer/DailyNotes/compare/{base}...{head}",
    "merges_url": "https://api.github.com/repos/Ayusummer/DailyNotes/merges",
    "archive_url": "https://api.github.com/repos/Ayusummer/DailyNotes/{archive_format}{/ref}",
    "downloads_url": "https://api.github.com/repos/Ayusummer/DailyNotes/downloads",
    "issues_url": "https://api.github.com/repos/Ayusummer/DailyNotes/issues{/number}",
    "pulls_url": "https://api.github.com/repos/Ayusummer/DailyNotes/pulls{/number}",
    "milestones_url": "https://api.github.com/repos/Ayusummer/DailyNotes/milestones{/number}",
    "notifications_url": "https://api.github.com/repos/Ayusummer/DailyNotes/notifications{?since,all,participating}",
    "labels_url": "https://api.github.com/repos/Ayusummer/DailyNotes/labels{/name}",
    "releases_url": "https://api.github.com/repos/Ayusummer/DailyNotes/releases{/id}",
    "deployments_url": "https://api.github.com/repos/Ayusummer/DailyNotes/deployments",
    "created_at": 1611240215,
    "updated_at": "2022-05-07T14:35:27Z",
    "pushed_at": 1662116194,
    "git_url": "git://github.com/Ayusummer/DailyNotes.git",
    "ssh_url": "git@github.com:Ayusummer/DailyNotes.git",
    "clone_url": "https://github.com/Ayusummer/DailyNotes.git",
    "svn_url": "https://github.com/Ayusummer/DailyNotes",
    "homepage": null,
    "size": 12385,
    "stargazers_count": 4,
    "watchers_count": 4,
    "language": "Jupyter Notebook",
    "has_issues": true,
    "has_projects": true,
    "has_downloads": true,
    "has_wiki": true,
    "has_pages": false,
    "forks_count": 0,
    "mirror_url": null,
    "archived": false,
    "disabled": false,
    "open_issues_count": 0,
    "license": {
      "key": "mit",
      "name": "MIT License",
      "spdx_id": "MIT",
      "url": "https://api.github.com/licenses/mit",
      "node_id": "MDc6TGljZW5zZTEz"
    },
    "allow_forking": true,
    "is_template": false,
    "web_commit_signoff_required": false,
    "topics": [

    ],
    "visibility": "public",
    "forks": 0,
    "open_issues": 0,
    "watchers": 4,
    "default_branch": "main",
    "stargazers": 4,
    "master_branch": "main"
  },
  "pusher": {
    "name": "Ayusummer",
    "email": "ayusummer233@qq.com"
  },
  "sender": {
    "login": "Ayusummer",
    "id": 59549826,
    "node_id": "MDQ6VXNlcjU5NTQ5ODI2",
    "avatar_url": "https://avatars.githubusercontent.com/u/59549826?v=4",
    "gravatar_id": "",
    "url": "https://api.github.com/users/Ayusummer",
    "html_url": "https://github.com/Ayusummer",
    "followers_url": "https://api.github.com/users/Ayusummer/followers",
    "following_url": "https://api.github.com/users/Ayusummer/following{/other_user}",
    "gists_url": "https://api.github.com/users/Ayusummer/gists{/gist_id}",
    "starred_url": "https://api.github.com/users/Ayusummer/starred{/owner}{/repo}",
    "subscriptions_url": "https://api.github.com/users/Ayusummer/subscriptions",
    "organizations_url": "https://api.github.com/users/Ayusummer/orgs",
    "repos_url": "https://api.github.com/users/Ayusummer/repos",
    "events_url": "https://api.github.com/users/Ayusummer/events{/privacy}",
    "received_events_url": "https://api.github.com/users/Ayusummer/received_events",
    "type": "User",
    "site_admin": false
  },
  "created": false,
  "deleted": false,
  "forced": false,
  "base_ref": null,
  "compare": "https://github.com/Ayusummer/DailyNotes/compare/af5ffecce599...da7a8f85a903",
  "commits": [
    {
      "id": "da7a8f85a9030e062cdc3edbc2076b16666818a1",
      "tree_id": "43709cefd32f1d9f45a77e233338961653e1d6ff",
      "distinct": true,
      "message": "webhook message - commit link",
      "timestamp": "2022-09-02T18:56:34+08:00",
      "url": "https://github.com/Ayusummer/DailyNotes/commit/da7a8f85a9030e062cdc3edbc2076b16666818a1",
      "author": {
        "name": "咸鱼型233",
        "email": "ayusummer233@qq.com",
        "username": "Ayusummer"
      },
      "committer": {
        "name": "GitHub",
        "email": "noreply@github.com",
        "username": "web-flow"
      },
      "added": [

      ],
      "removed": [

      ],
      "modified": [

      ]
    }
  ],
  "head_commit": {
    "id": "da7a8f85a9030e062cdc3edbc2076b16666818a1",
    "tree_id": "43709cefd32f1d9f45a77e233338961653e1d6ff",
    "distinct": true,
    "message": "webhook message - commit link",
    "timestamp": "2022-09-02T18:56:34+08:00",
    "url": "https://github.com/Ayusummer/DailyNotes/commit/da7a8f85a9030e062cdc3edbc2076b16666818a1",
    "author": {
      "name": "咸鱼型233",
      "email": "ayusummer233@qq.com",
      "username": "Ayusummer"
    },
    "committer": {
      "name": "GitHub",
      "email": "noreply@github.com",
      "username": "web-flow"
    },
    "added": [

    ],
    "removed": [

    ],
    "modified": [

    ]
  }
}
```

---

### Gitlab Repo Webhook

`Headers`:

```
Content-Type: application/json
User-Agent: GitLab/15.4.0-pre
X-Gitlab-Event: Push Hook
X-Gitlab-Event-UUID: ***
```

`Pyload`:

```json
{
  "object_kind": "push",
  "event_name": "push",
  "before": "95790bf891e76fee5e1747ab589903a6a1f80f22",
  "after": "da1560886d4f094c3e6c9ef40349f7d38b5d27d7",
  "ref": "refs/heads/master",
  "checkout_sha": "***",
  "message": "Hello World",
  "user_id": 4,
  "user_name": "John Smith",
  "user_email": "john@example.com",
  "user_avatar": "https://s.gravatar.com/avatar/d4c74594d841139328695756648b6bd6?s=8://s.gravatar.com/avatar/d4c74594d841139328695756648b6bd6?s=80",
  "project_id": 15,
  "project": {
    "id": 15,
    "name": "gitlab",
    "description": "",
    "web_url": "http://test.example.com/gitlab/gitlab",
    "avatar_url": "https://s.gravatar.com/avatar/d4c74594d841139328695756648b6bd6?s=8://s.gravatar.com/avatar/d4c74594d841139328695756648b6bd6?s=80",
    "git_ssh_url": "git@test.example.com:gitlab/gitlab.git",
    "git_http_url": "http://test.example.com/gitlab/gitlab.git",
    "namespace": "gitlab",
    "visibility_level": 0,
    "path_with_namespace": "gitlab/gitlab",
    "default_branch": "master"
  },
  "commits": [
    {
      "id": "c5feabde2d8cd023215af4d2ceeb7a64839fc428",
      "message": "Add simple search to projects in public area\n\ncommit message body",
      "title": "Add simple search to projects in public area",
      "timestamp": "2013-05-13T18:18:08+00:00",
      "url": "https://test.example.com/gitlab/gitlab/-/commit/c5feabde2d8cd023215af4d2ceeb7a64839fc428",
      "author": {
        "name": "Test User",
        "email": "test@example.com"
      }
    }
  ],
  "total_commits_count": 1,
  "push_options": {
    "ci": {
      "skip": true
    }
  }
}
```

---

## HMAC 算法



