# Tavily Search Toolkit for OpenClaw

A practical Tavily skill for OpenClaw with **search / extract / crawl / map** in one script.

一个面向 OpenClaw 的 Tavily 实用技能包，统一支持 **search / extract / crawl / map**。

Only **1 step** to start: send one prompt to OpenClaw, then follow guided onboarding.

只要 **1 步**就能开始：把提示词发给 OpenClaw，后续按引导完成配置。

---

## Step 1: Install / 安装

### Recommended one-shot prompt for beginners / 新手推荐一键提示词

Send this to your OpenClaw agent:

把下面整段发给你的 OpenClaw：

```text
Install the Tavily Search skill from GitHub into my OpenClaw workspace skills directory (NOT .agents).

Requirements:
1) Target directory must be: ~/.openclaw/workspace/skills/tavily-search
2) Clone source: https://github.com/plabzzxx/openclaw-tavily-search
3) Ensure script exists at: ~/.openclaw/workspace/skills/tavily-search/scripts/tavily_search.mjs
4) Create ~/.openclaw/.env if missing, and ensure this placeholder line exists:
   TAVILY_API_KEY=
5) Return a short verification report with absolute paths and whether each step succeeded.
6) Add a memory preference:
   - When web_search (Brave) is unavailable, use tavily-search skill first.
   - For general web lookup tasks, try tavily-search before giving up.
7) Stop here and ask the user:
   "Tavily skill is installed. Do you want guided setup for Tavily API key now?"
```

What this one-shot prompt does:

这个一键提示词会做这些事情：

- Install the skill into the correct workspace path (not `.agents`).
- 把技能安装到正确的 workspace 路径（不会装到 `.agents`）。
- Ensure the main script file exists and is executable.
- 确认主脚本存在且可执行。
- Create `~/.openclaw/.env` if missing and add `TAVILY_API_KEY=` placeholder.
- 如果缺少 `~/.openclaw/.env`，会创建并写入 `TAVILY_API_KEY=` 占位符。
- Return a short verification report so beginners can see exactly what changed.
- 返回简短验证报告，让新手清楚看到改了哪些路径和步骤。
- Add a memory preference so Tavily is used first when Brave web_search is unavailable.
- 写入一条记忆偏好：当 Brave web_search 不可用时优先使用 Tavily skill。
- Stop after install and ask whether the user wants guided Tavily API key setup.
- 安装完成后先停下，询问用户是否需要引导配置 Tavily API key。

### Manual install / 手动安装

```bash
mkdir -p ~/.openclaw/workspace/skills
cd ~/.openclaw/workspace/skills
git clone https://github.com/plabzzxx/openclaw-tavily-search tavily-search
```

---

## Step 2: Setup API Key / 配置 API Key

OpenClaw can guide this step interactively after installation.

安装完成后，OpenClaw 会通过自然语言引导你完成这一步。

Recommended guided flow / 推荐引导流程：

1) Open https://tavily.com and sign up / sign in.

1）打开 https://tavily.com ，注册或登录账号。

2) Create/copy your Tavily API key.

2）创建并复制 Tavily API key。

3) Choose one of the two setup methods:

3）二选一完成配置：

- **Safer (recommended):** paste key manually into `~/.openclaw/.env`
- **更安全（推荐）：** 手动写入 `~/.openclaw/.env`

```env
TAVILY_API_KEY=tvly-xxxx
```

- **Convenient:** send key to OpenClaw and let it write for you
- **更方便：** 直接把 key 发给 OpenClaw 让它代填

> Manual local edit is safer than sharing secrets in chat.
>
> 本地手动编辑通常比在聊天中传递密钥更安全。

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
