# CHANGELOG

- 2022.11.7
  - feat
    - 新增 workflow 以及 deployment 和 pages 相关事件支持, 但只保留对 page_build 事件的处理  
      > 因为其他事件刷屏太严重了  
- 2022.9.3
  - feat
    - 新增对 Webhook 初始化时的 ping 事件的支持
    - 新增对 branch or tag create 事件的支持
  - fix
    - 修复多个 Push 事件只显示一个的问题
    - 修复单个 commit 推送文本为 commits 的问题