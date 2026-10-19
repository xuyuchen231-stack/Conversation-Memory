# Conversation Memory

试用版：逐条归档对话，建立分类索引与有证据的风格档案，让新聊天接续工作。

## 使用

将 `conversation-memory` 文件夹安装至使用环境的技能目录。Codex 本机可放入 `~/.codex/skills/`；重新打开聊天后确认技能是否可发现。调用：

`请使用 $conversation-memory，把这些对话完整归档并生成新聊天接续包。`

不支持技能安装的聊天：上传私人接续包，粘贴 `conversation-memory/references/prompts.md` 内的接续提示词。

本地 Codex 日志转换：

```sh
python conversation-memory/scripts/archive_codex.py /path/to/session.jsonl --out /path/to/private-memory
```

转换器仅处理实际存在的 user/assistant message 记录。保留消息原始记录与规范化内容，记录源文件哈希；不备份系统指令、隐藏推理或工具日志。附件实体需要单独备份。活动聊天仅为截止时快照。

ChatGPT 批量记录需提供目标账号导出文件或可访问的完整记录；当前转换器不直接解析 ChatGPT 导出，须检查实际格式后适配。不同账号的私人链接不提供访问授权。

技能不会永久训练模型、自动读取其他账号、保证完全复刻风格，或自动开始后台监测。

## 发布边界

公开仓库：[xuyuchen231-stack/conversation-archive](https://github.com/xuyuchen231-stack/conversation-archive)。私人归档保存在仓库之外。当前为试用版；GitHub 源码发布不表示已进入技能商店。

技能格式参考：[OpenAI Skills](https://developers.openai.com/plugins/concepts/skills)。
