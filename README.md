# Tavily Search Toolkit for OpenClaw

A practical Tavily skill for OpenClaw with **search / extract / crawl / map** in one script.

一个面向 OpenClaw 的 Tavily 实用技能包，统一支持 **search / extract / crawl / map**。

---

## Install / 安装

Tell your OpenClaw agent:

把下面这句话直接发给你的 OpenClaw：

```text
Please install this skill from GitHub: https://github.com/plabzzxx/openclaw-tavily-search
```

For manual copy/migration, copy this repository folder into your OpenClaw workspace skills directory.

如果你要手动迁移，直接把这个仓库复制到目标 OpenClaw 的 skills 目录即可。

---

## Setup API Key / 配置 API Key

Step 1: Get a Tavily API key from the official website: https://tavily.com

第 1 步：去 Tavily 官网申请 API Key：https://tavily.com

Step 2: Put your key in `~/.openclaw/.env`:

第 2 步：把 key 写进 `~/.openclaw/.env`：

```env
TAVILY_API_KEY=tvly-xxxx
```

You can also send your key to your agent and let it write config for you, but this is less secure.

你也可以把 key 发给 Agent 让它代填，但安全性更低，不推荐。

---

## Why Tavily / 为什么用 Tavily

Tavily is a strong alternative when Brave web_search is unavailable or undesired.

当 Brave web_search 不可用或不想使用时，Tavily 是非常实用的替代方案。

Many users choose Tavily because it has a free quota tier (subject to Tavily policy updates).

很多用户会选 Tavily，因为通常有一定免费额度（以 Tavily 官方实时政策为准）。

---

## Natural language usage / 自然语言触发示例

You can ask your OpenClaw naturally:

你可以直接自然语言让 OpenClaw 调用：

- "Search the web for OpenClaw multi-agent best practices, 5 results."
- “搜一下 OpenClaw 多智能体最佳实践，给我 5 条。”

- "Search Chow Tai Fook, include only official domains."
- “搜周大福，只保留官网域名结果。”

- "Extract this URL and summarize in bullet points."
- “把这个链接抽取正文并按要点总结。”

- "Crawl this docs site with depth 2 and give me a markdown digest."
- “爬这个文档站，深度 2，给我 markdown 摘要。”

---

## Basic mode vs advanced mode / 基础模式与进阶模式

For most users, `search` is enough for daily web lookup.

对大多数用户来说，`search` 模式足够覆盖日常联网检索。

Advanced workflows use `extract / crawl / map` when you need structured site intelligence.

当你需要更结构化的网站情报时，再用 `extract / crawl / map` 进阶能力。

---

## CLI examples / 命令示例

```bash
# Search with brave-like output
node scripts/tavily_search.mjs search --query "OpenClaw" --max-results 5 --format brave

# Search with domain include/exclude
node scripts/tavily_search.mjs search --query "周大福" \
  --include-domains ctf.com.cn,ctfmall.com,chowtaifook.com \
  --exclude-domains facebook.com,weibo.com --format brave

# Extract content from URLs
node scripts/tavily_search.mjs extract --urls https://docs.openclaw.ai --content-format markdown --format md

# Crawl / Map
node scripts/tavily_search.mjs crawl --url docs.tavily.com --max-depth 2 --limit 30 --format md
node scripts/tavily_search.mjs map --url docs.openclaw.ai --max-depth 2 --limit 40 --format md
```

---

## Security notes / 安全说明

- Prefer storing keys in local `.env` instead of chat messages.
- Use `--no-proxy` only when direct network is available.
- Keep result limits small to reduce token/cost.

- 建议把 key 存在本地 `.env`，尽量不要走聊天传输。
- 只有在直连可用时才使用 `--no-proxy`。
- 结果数量建议保持较小，减少 token 与成本。
